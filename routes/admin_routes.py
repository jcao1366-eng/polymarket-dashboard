from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from services.admin_service import (
    verify_admin, get_orders, get_all_products, update_order_status,
    update_order_tracking, get_product, create_product, update_product,
    delete_product, create_category, delete_category, search_orders, search_products
)
from services.product_service import get_categories
from functools import wraps

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated

# ─── Context processor: inject pending count into all admin pages ───
@admin_bp.context_processor
def inject_admin_context():
    from models import Order
    pending_count = Order.query.filter(Order.status == "pending").count()
    return dict(pending_count=pending_count)

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))
    if request.method == "POST":
        if verify_admin(request.form.get("username", ""), request.form.get("password", "")):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password. Please try again.", "error")
    return render_template("admin/login.html")

@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))

# ─── Dashboard ────────────────────────────────────────
@admin_bp.route("/")
@admin_required
def dashboard():
    from models import Product, Order, PageView
    from sqlalchemy import func, cast, Date
    from datetime import datetime, timedelta, timezone

    total_products = Product.query.count()
    active_products = Product.query.filter(Product.is_active == True).count()
    total_orders = Order.query.count()
    pending_orders_count = Order.query.filter(Order.status == "pending").count()

    # Revenue stats
    revenue_result = Order.query.with_entities(func.sum(Order.total)).scalar()
    total_revenue = float(revenue_result) if revenue_result else 0.0
    avg_order = total_revenue / total_orders if total_orders > 0 else 0.0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    featured_products = Product.query.filter(Product.is_featured == True).order_by(Product.created_at.desc()).limit(4).all()

    # ─── Analytics: Today's visits ───
    now_utc = datetime.now(timezone.utc)
    today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    last_7d_start = today_start - timedelta(days=7)

    today_views = PageView.query.filter(PageView.created_at >= today_start).count()
    today_unique = PageView.query.filter(PageView.created_at >= today_start).with_entities(func.count(func.distinct(PageView.ip))).scalar() or 0
    yesterday_views = PageView.query.filter(PageView.created_at >= yesterday_start, PageView.created_at < today_start).count()
    week_views = PageView.query.filter(PageView.created_at >= last_7d_start).count()
    week_unique = PageView.query.filter(PageView.created_at >= last_7d_start).with_entities(func.count(func.distinct(PageView.ip))).scalar() or 0

    # Top pages this week
    top_pages = PageView.query.filter(PageView.created_at >= last_7d_start).with_entities(
        PageView.path, func.count(PageView.id).label("hits")
    ).group_by(PageView.path).order_by(func.count(PageView.id).desc()).limit(5).all()

    # Daily trend (last 7 days)
    daily_trend = []
    for i in range(6, -1, -1):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_views = PageView.query.filter(PageView.created_at >= day_start, PageView.created_at < day_end).count()
        daily_trend.append({
            "date": day_start.strftime("%m/%d"),
            "views": day_views,
        })

    # Countries
    top_countries = PageView.query.filter(PageView.created_at >= last_7d_start).filter(
        PageView.country != ""
    ).with_entities(
        PageView.country, func.count(PageView.id).label("hits")
    ).group_by(PageView.country).order_by(func.count(PageView.id).desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        active_page="dashboard",
        total_products=total_products,
        active_products=active_products,
        total_orders=total_orders,
        pending_orders_count=pending_orders_count,
        total_revenue=total_revenue,
        avg_order=avg_order,
        recent_orders=recent_orders,
        featured_products=featured_products,
        # analytics
        today_views=today_views,
        today_unique=today_unique,
        yesterday_views=yesterday_views,
        week_views=week_views,
        week_unique=week_unique,
        top_pages=top_pages,
        daily_trend=daily_trend,
        top_countries=top_countries,
    )

# ─── Orders ───────────────────────────────────────────
@admin_bp.route("/orders")
@admin_required
def orders():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    orders = search_orders(q=q, status=status, page=page)
    return render_template("admin/orders.html", active_page="orders", orders=orders)

@admin_bp.route("/orders/<int:order_id>")
@admin_required
def order_detail(order_id):
    from models import Order, OrderItem
    order = Order.query.get_or_404(order_id)
    items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template("admin/order_detail.html", active_page="orders", order=order, items=items)

@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def update_status(order_id):
    status = request.form.get("status", "pending")
    update_order_status(order_id, status)
    return redirect(request.referrer or url_for("admin.orders"))

@admin_bp.route("/orders/<int:order_id>/tracking", methods=["POST"])
@admin_required
def update_tracking(order_id):
    tracking = request.form.get("tracking_number", "").strip()
    update_order_tracking(order_id, tracking)
    return redirect(request.referrer or url_for("admin.order_detail", order_id=order_id))

# ─── Products ──────────────────────────────────────────
@admin_bp.route("/products")
@admin_required
def products():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    prods = search_products(q=q, status=status)
    categories = get_categories()
    return render_template("admin/products.html", active_page="products", products=prods, categories=categories)

@admin_bp.route("/products/new", methods=["GET", "POST"])
@admin_required
def new_product():
    categories = get_categories()
    if request.method == "POST":
        try:
            data = {
                "name": request.form.get("name", ""),
                "slug": request.form.get("slug", ""),
                "base_price": request.form.get("base_price", 0),
                "compare_price": request.form.get("compare_price", 0),
                "cost_price": request.form.get("cost_price", 0),
                "description": request.form.get("description", ""),
                "description_en": request.form.get("description_en", ""),
                "supplier_url": request.form.get("supplier_url", ""),
                "image_url": request.form.get("image_url", ""),
                "images": request.form.get("images", ""),
                "is_active": request.form.get("is_active") == "on",
                "is_featured": request.form.get("is_featured") == "on",
                "seo_title": request.form.get("seo_title", ""),
                "seo_description": request.form.get("seo_description", ""),
                "categories": request.form.getlist("categories"),
            }
            p = create_product(data)
            flash(f"Product '{p.name}' created successfully!", "success")
            return redirect(url_for("admin.edit_product", product_id=p.id))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    return render_template("admin/product_form.html", active_page="product_form", categories=categories, product=None)

@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    p = get_product(product_id)
    categories = get_categories()
    if request.method == "POST":
        try:
            data = {
                "name": request.form.get("name", ""),
                "slug": request.form.get("slug", ""),
                "base_price": request.form.get("base_price", 0),
                "compare_price": request.form.get("compare_price", 0),
                "cost_price": request.form.get("cost_price", 0),
                "description": request.form.get("description", ""),
                "description_en": request.form.get("description_en", ""),
                "supplier_url": request.form.get("supplier_url", ""),
                "image_url": request.form.get("image_url", ""),
                "images": request.form.get("images", ""),
                "is_active": request.form.get("is_active") == "on",
                "is_featured": request.form.get("is_featured") == "on",
                "seo_title": request.form.get("seo_title", ""),
                "seo_description": request.form.get("seo_description", ""),
                "categories": request.form.getlist("categories"),
            }
            update_product(product_id, data)
            flash(f"Product '{p.name}' updated!", "success")
            return redirect(url_for("admin.edit_product", product_id=product_id))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    return render_template("admin/product_form.html", active_page="product_form", categories=categories, product=p)

@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def remove_product(product_id):
    delete_product(product_id)
    flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))

# ─── Categories ───────────────────────────────────────
@admin_bp.route("/categories")
@admin_required
def categories():
    cats = get_categories()
    return render_template("admin/categories.html", active_page="categories", categories=cats)

@admin_bp.route("/categories/new", methods=["POST"])
@admin_required
def new_category():
    try:
        create_category(request.form.to_dict())
        flash("Category created!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for("admin.categories"))

@admin_bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@admin_required
def remove_category(cat_id):
    delete_category(cat_id)
    flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))
