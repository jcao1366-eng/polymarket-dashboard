"""Flask Web Server with reverse proxy for Polymarket APIs.
Serves the trading dashboard and proxies all Polymarket requests
so that clients behind the GFW can access market data.

Endpoints:
  GET  /                        — Dashboard HTML
  GET  /api/trending            — Trending markets (proxied)
  GET  /api/search?q=           — Search markets (proxied)
  GET  /api/book/<token_id>     — Order book (proxied)
  GET  /api/resolve?slug=       — Resolve market (proxied)
  GET  /api/price-history/<tid> — Price history (proxied)
  POST /api/clob-derive         — Derive API key (proxied)
  POST /api/clob-order          — Place order (proxied)
  POST /api/clob-cancel         — Cancel order (proxied)
  GET  /api/positions           — Positions (proxied)
  GET  /api/orders              — Orders (proxied)
  POST /api/tunnel-url          — Return public tunnel URL
  GET  /api/analytics           — 访问统计 & 日志分析
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import requests
from flask import Flask, request, jsonify, send_file, Response, g

# Project root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
DATA_API = "https://data-api.polymarket.com"

app = Flask(__name__)

# =================== 访问日志系统 ===================

# 云环境（Render 等）只能写 /tmp，本地用项目目录
if os.environ.get("RENDER") or not os.access(str(ROOT), os.W_OK):
    _LOG_BASE = Path("/tmp")
else:
    _LOG_BASE = ROOT
ACCESS_LOG_DIR = _LOG_BASE / "logs"
ACCESS_LOG_FILE = ACCESS_LOG_DIR / "access.jsonl"
ACCESS_LOG_DIR.mkdir(exist_ok=True, parents=True)

# 内存中的访问记录（用于实时分析）
_access_records = []          # 全部记录（最多保留 10000 条）
_access_lock = threading.Lock()
_startup_time = datetime.now(timezone(timedelta(hours=8)))  # 服务器启动时间
_total_requests = 0

# 需要排除的路径（不记录内部请求）
_SKIP_PATHS = {"/api/health", "/api/analytics"}


def _parse_cf_headers():
    """从 Cloudflare 转发的请求头中提取真实 IP 和地理位置。"""
    # Cloudflare Tunnel 会注入这些头信息
    cf_ip = request.headers.get("CF-Connecting-IP")
    real_ip = request.headers.get("X-Forwarded-For", cf_ip or request.remote_addr)
    if "," in real_ip:
        real_ip = real_ip.split(",")[0].strip()

    return {
        "ip": real_ip,
        "country": request.headers.get("CF-IPCountry", "??"),
        "city": request.headers.get("CF-IPCity", ""),
        "asn": request.headers.get("CF-Ray", ""),  # CF-Ray 作为连接标识
        "via_cloudflare": bool(cf_ip),
    }


def _classify_user_agent(ua_string):
    """简单分类 User-Agent。"""
    ua_lower = (ua_string or "").lower()
    if not ua_string or ua_string == "-":
        return "unknown"
    if any(b in ua_lower for b in ["bot", "crawler", "spider", "curl", "wget", "python", "http"]):
        return "bot"
    if "mobile" in ua_lower or any(m in ua_lower for m in ["iphone", "android", "ipad"]):
        return "mobile"
    return "desktop"


def _record_access(status_code, response_time_ms):
    """记录一次访问到日志文件和内存。"""
    global _total_requests

    path = request.path
    method = request.method

    # 跳过内部健康检查等
    if path in _SKIP_PATHS:
        return

    cf_info = _parse_cf_headers()
    ua_raw = request.headers.get("User-Agent", "-")
    now = datetime.now(timezone(timedelta(hours=8)))

    entry = {
        "time": now.isoformat(),
        "timestamp": time.time(),
        "method": method,
        "path": path,
        "query_string": dict(request.args) if request.args else {},
        "status_code": status_code,
        "response_ms": round(response_time_ms, 1),
        "ip": cf_info["ip"],
        "country": cf_info["country"],
        "city": cf_info["city"],
        "via_cloudflare": cf_info["via_cloudflare"],
        "user_agent": ua_raw[:200],  # 截断过长的 UA
        "device_type": _classify_user_agent(ua_raw),
        "referrer": request.headers.get("Referer", "")[:300],
    }

    # 写入文件（追加 JSONL）
    try:
        with open(ACCESS_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # 写入内存（带锁）
    with _access_lock:
        _access_records.append(entry)
        _total_requests += 1
        # 限制内存占用
        if len(_access_records) > 10000:
            _access_records[:] = _access_records[-5000:]


@app.before_request
def _before_req():
    g.start_time = time.time()


@app.after_request
def _after_req(response):
    rt = (time.time() - g.start_time) * 1000 if hasattr(g, "start_time") else 0
    _record_access(response.status_code, rt)

    # 在响应头中加入统计信息（方便调试）
    response.headers["X-Request-ID"] = str(int(time.time() * 1000))
    return response


def _load_all_logs():
    """从文件加载所有历史访问记录。"""
    records = []
    if ACCESS_LOG_FILE.exists():
        try:
            with open(ACCESS_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
    # 合并内存中的最新记录
    with _access_lock:
        mem_ids = {r.get("timestamp") for r in _access_records}
        for r in records:
            if r.get("timestamp") not in mem_ids:
                _access_records.append(r)
        _access_records.sort(key=lambda x: x.get("timestamp", 0))
        if len(_access_records) > 10000:
            _access_records[:] = _access_records[-5000:]
    return _access_records


def _compute_analytics(records):
    """计算访问统计数据。"""
    if not records:
        return {
            "summary": {"total_visits": 0, "unique_visitors": 0, "total_pageviews": 0},
            "timeline": [], "top_pages": [], "top_countries": [],
            "devices": {}, "recent": [],
        }

    # 基础统计
    total_pv = len(records)
    unique_ips = set(r["ip"] for r in records if r.get("ip"))
    # 按会话估算：同一IP间隔>30分钟算新访客
    sessions = []
    ip_last_seen = {}
    for r in sorted(records, key=lambda x: x.get("timestamp", 0)):
        ip = r.get("ip", "")
        ts = r.get("timestamp", 0)
        if ip and (ip not in ip_last_seen or ts - ip_last_seen[ip] > 1800):
            sessions.append(r)
        ip_last_seen[ip] = ts

    # 时间线分布（按小时）
    hourly = Counter()
    daily = Counter()
    for r in records:
        t = r.get("time", "")
        try:
            dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
            # 转换为北京时间
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            bj_t = dt.astimezone(timezone(timedelta(hours=8)))
            hourly[f"{bj_t.hour:02d}:00"] += 1
            daily[bj_t.strftime("%m-%d")] += 1
        except Exception:
            pass

    # 热门页面
    page_views = Counter()
    page_uv = defaultdict(set)
    for r in records:
        p = r.get("path", "/")
        page_views[p] += 1
        if r.get("ip"):
            page_uv[p].add(r["ip"])

    top_pages = [
        {"path": p, "pv": c, "uv": len(page_uv[p])}
        for p, c in page_views.most_common(15)
    ]

    # 国家/地区分布
    country_count = Counter(r.get("country", "??") for r in records)
    top_countries = [{"country": c, "count": n} for c, n in country_count.most_common(10)]

    # 设备类型
    device_count = Counter(r.get("device_type", "unknown") for r in records)

    # User-Agent 统计（去重简化）
    ua_counter = Counter()
    for r in records:
        ua = r.get("user_agent", "")[:80]
        ua_counter[ua] += 1
    top_uas = [{"ua": u, "count": c} for u, c in ua_counter.most_common(10)]

    # 最近 20 条访问
    recent = [
        {
            "time": r.get("time", "")[11:19],  # 只取时分秒
            "path": r.get("path", ""),
            "method": r.get("method", ""),
            "ip": r.get("ip", "")[:3] + "***" if len(r.get("ip", "")) > 3 else r.get("ip", ""),
            "country": r.get("country", "??"),
            "device": r.get("device_type", "?"),
            "status": r.get("status_code"),
            "ms": r.get("response_ms", 0),
        }
        for r in records[-20:]
    ]

    # 操作类型统计（API调用 vs 页面浏览）
    api_calls = [r for r in records if r.get("path", "").startswith("/api/")]
    page_browses = [r for r in records if not r.get("path", "").startswith("/api/")]
    api_breakdown = Counter(r.get("path") for r in api_calls)

    return {
        "summary": {
            "total_pageviews": total_pv,
            "unique_visitors": len(unique_ips),
            "estimated_sessions": len(sessions),
            "api_calls": len(api_calls),
            "page_browses": len(page_browses),
            "server_started": _startup_time.isoformat(),
            "uptime_seconds": round((datetime.now(timezone(timedelta(hours=8))) - _startup_time).total_seconds()),
        },
        "timeline_hourly": dict(sorted(hourly.items())),
        "timeline_daily": dict(sorted(daily.items())),
        "top_pages": top_pages,
        "top_countries": top_countries,
        "devices": dict(device_count.most_common()),
        "top_user_agents": top_uas,
        "api_breakdown": {k: v for k, v in api_breakdown.most_common(15)},
        "recent_visits": recent[::-1],  # 最新的在前
    }

# =================== Proxy Helpers ===================

def proxy_get(target_url, params=None):
    """Forward GET request to Polymarket and stream response back."""
    try:
        resp = requests.get(target_url, params=params, timeout=15,
                            headers={"Accept": "application/json",
                                     "User-Agent": "PolymarketProxy/1.0"})
        return Response(resp.content, status=resp.status_code,
                        content_type=resp.headers.get("Content-Type", "application/json"))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502

def proxy_post(target_url, json_data=None):
    """Forward POST request to Polymarket."""
    try:
        resp = requests.post(target_url, json=json_data, timeout=15,
                             headers={"Content-Type": "application/json",
                                      "User-Agent": "PolymarketProxy/1.0"})
        return Response(resp.content, status=resp.status_code,
                        content_type=resp.headers.get("Content-Type", "application/json"))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502


# =================== Pages ===================

@app.route("/")
def index():
    return send_file(str(ROOT / "dist" / "index.html"))


# =================== Proxied Public API ===================

@app.route("/api/trending")
def api_trending():
    limit = request.args.get("limit", 25, type=int)
    return proxy_get(f"{GAMMA_API}/markets", params={
        "closed": "false",
        "active": "true",
        "order": "volume24hr",
        "ascending": "false",
        "limit": limit,
    })


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    return proxy_get(f"{GAMMA_API}/markets", params={
        "closed": "false",
        "active": "true",
        "limit": 25,
        "query": q,
    })


@app.route("/api/book/<token_id>")
def api_book(token_id):
    return proxy_get(f"{CLOB_API}/book", params={"token_id": token_id})


@app.route("/api/resolve")
def api_resolve():
    slug = request.args.get("slug", "")
    if not slug:
        return jsonify({"error": "Missing slug"}), 400
    return proxy_get(f"{GAMMA_API}/markets", params={
        "slug": slug,
        "closed": "false",
    })


@app.route("/api/price-history/<token_id>")
def api_price_history(token_id):
    interval = request.args.get("interval", "1h")
    limit = request.args.get("limit", 100, type=int)
    return proxy_get(f"{DATA_API}/prices/{token_id}", params={
        "interval": interval,
        "limit": limit,
    })


@app.route("/api/market/<condition_id>")
def api_market(condition_id):
    return proxy_get(f"{GAMMA_API}/markets", params={
        "condition_id": condition_id,
    })


# =================== Proxied CLOB Trading API ===================

@app.route("/api/clob-derive", methods=["POST"])
def clob_derive():
    return proxy_post(f"{CLOB_API}/derive-api-key", request.json)


@app.route("/api/clob-order", methods=["POST"])
def clob_order():
    return proxy_post(f"{CLOB_API}/order", request.json)


@app.route("/api/clob-cancel", methods=["POST"])
def clob_cancel():
    order_id = (request.json or {}).get("orderID", "")
    return proxy_post(f"{CLOB_API}/cancel", {"orderID": order_id})


@app.route("/api/clob-cancel-all", methods=["POST"])
def clob_cancel_all():
    market = (request.json or {}).get("market", "")
    data = {"market": market} if market else {}
    return proxy_post(f"{CLOB_API}/cancel-all", data)


@app.route("/api/positions")
def api_positions():
    return proxy_get(f"{CLOB_API}/positions")


@app.route("/api/orders")
def api_orders():
    market = request.args.get("market", "")
    return proxy_get(f"{CLOB_API}/orders", params={"market": market} if market else None)


@app.route("/api/balance")
def api_balance():
    address = request.args.get("address", "")
    if not address:
        return jsonify({"error": "Missing address"}), 400
    return proxy_get(f"{CLOB_API}/balance", params={"address": address})


# =================== Health / Info ===================

@app.route("/api/health")
def health():
    # Check if Polymarket is reachable from server
    try:
        r = requests.get(f"{GAMMA_API}/markets", params={"limit": 1, "closed": "false"},
                         timeout=5)
        api_ok = r.status_code == 200
    except:
        api_ok = False
    return jsonify({"status": "ok", "polymarket_reachable": api_ok})


# =================== 访问分析 API ===================

@app.route("/api/analytics")
def analytics():
    """返回网站访问统计和分析数据。"""
    # 支持查询参数
    limit = min(request.args.get("limit", 0, type=int), 500)  # 0=全部

    records = _load_all_logs()
    if limit > 0:
        records = records[-limit:]

    data = _compute_analytics(records)

    # 原始记录（可选，默认不返回）
    if request.args.get("raw", "") == "1":
        data["raw_records"] = records[-50:]  # 最多返回50条原始记录

    return jsonify(data)


@app.route("/api/analytics/visitors")
def analytics_visitors():
    """返回访客列表（脱敏IP）。"""
    records = _load_all_logs()
    visitors = defaultdict(lambda: {"first_visit": None, "last_visit": None,
                                    "pageviews": 0, "pages": [], "country": "??"})
    for r in records:
        ip = r.get("ip", "unknown")
        v = visitors[ip]
        t = r.get("time", "")
        if not v["first_visit"] or t < v["first_visit"]:
            v["first_visit"] = t
        if not v["last_visit"] or t > v["last_visit"]:
            v["last_visit"] = t
        v["pageviews"] += 1
        p = r.get("path", "/")
        if p not in v["pages"]:
            v["pages"].append(p)
        if r.get("country") and r["country"] != "??":
            v["country"] = r["country"]

    result = []
    for ip, info in sorted(visitors.items(), key=lambda x: -x[1]["pageviews"]):
        # IP 脱敏：只显示前3段
        masked_ip = ".".join(ip.split(".")[:2]) + ".***" if ip.count(".") >= 2 else "***"
        result.append({
            "ip_masked": masked_ip,
            "country": info["country"],
            "pageviews": info["pageviews"],
            "pages_visited": len(info["pages"]),
            "first_visit": (info["first_visit"] or "")[11:19],
            "last_visit": (info["last_visit"] or "")[11:19],
            "top_pages": info["pages"][:5],
        })

    return jsonify({
        "total_visitors": len(result),
        "visitors": result[:100],  # 最多100个访客
    })


# =================== Run ===================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n{'='*50}")
    print(f"  Polymarket Trading Bot - Proxy Mode")
    print(f"  Local:    http://localhost:{port}")
    print(f"  Network:  http://0.0.0.0:{port}")
    print(f"  Access Log: {ACCESS_LOG_FILE.name}")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
