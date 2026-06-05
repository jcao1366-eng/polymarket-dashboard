from flask import Blueprint, jsonify, request
from services.product_service import get_products
from services.cart_service import get_cart_count, get_cart_total
from services.currency_service import RATES, SYMBOLS

api_bp = Blueprint("api", __name__)

@api_bp.route("/products")
def api_products():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 12, type=int)
    products = get_products(page=page, per_page=per_page)
    data = [{"id": p.id, "name": p.name, "slug": p.slug, "price": p.base_price, "image": p.image_url} for p in products.items]
    return jsonify({"products": data, "total": products.total, "pages": products.pages})

@api_bp.route("/cart/info")
def cart_info():
    currency = request.args.get("currency", "USD")
    return jsonify({"count": get_cart_count(), "total": get_cart_total(currency), "currency": currency})

@api_bp.route("/currencies")
def currencies():
    return jsonify({"rates": RATES, "symbols": SYMBOLS})

@api_bp.route("/shipping-rates")
def shipping_rates():
    country = request.args.get("country", "US")
    rates = {"US": 5.99, "CA": 9.99, "GB": 12.99, "DE": 14.99, "AU": 15.99}
    return jsonify({"rate": rates.get(country, 15.99)})
