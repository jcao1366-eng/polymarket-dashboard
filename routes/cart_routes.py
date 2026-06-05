from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from services.cart_service import get_cart, get_cart_count, get_cart_total, add_to_cart, update_cart_item, remove_from_cart, clear_cart

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart")
def cart_page():
    items = get_cart()
    currency = request.args.get("currency", "USD")
    total = get_cart_total(currency)
    from services.currency_service import format_price
    return render_template("pages/cart.html", items=items, total=total, currency=currency, format_price=format_price)

@cart_bp.route("/cart/add", methods=["POST"])
def add():
    product_id = request.form.get("product_id", type=int)
    variant_id = request.form.get("variant_id", type=int) or None
    quantity = request.form.get("quantity", 1, type=int)
    add_to_cart(product_id, variant_id, quantity)
    return jsonify({"count": get_cart_count()})

@cart_bp.route("/cart/update/<int:item_id>", methods=["POST"])
def update(item_id):
    quantity = request.form.get("quantity", type=int)
    update_cart_item(item_id, quantity)
    return jsonify({"count": get_cart_count()})

@cart_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove(item_id):
    remove_from_cart(item_id)
    return jsonify({"count": get_cart_count()})

@cart_bp.route("/cart/clear", methods=["POST"])
def clear():
    clear_cart()
    return redirect(url_for("cart.cart_page"))
