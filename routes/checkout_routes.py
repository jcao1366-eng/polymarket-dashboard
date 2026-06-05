from flask import Blueprint, render_template, request, redirect, url_for
from services.checkout_service import create_checkout_session
from services.cart_service import get_cart_count, get_cart_total
import stripe

checkout_bp = Blueprint("checkout", __name__)

@checkout_bp.route("/checkout")
def checkout_page():
    from flask import current_app
    currency = request.args.get("currency", "USD")
    total = get_cart_total(currency)
    from services.currency_service import format_price, SYMBOLS
    pk = current_app.config.get("STRIPE_PUBLISHABLE_KEY", "")
    return render_template("pages/checkout.html", total=total, currency=currency, format_price=format_price, symbol=SYMBOLS.get(currency, "$"), pk=pk)

@checkout_bp.route("/checkout/create", methods=["POST"])
def create():
    email = request.form.get("email", "")
    currency = request.form.get("currency", "USD")
    url, err = create_checkout_session(email, currency)
    if err:
        return redirect(url_for("cart.cart_page"))
    return redirect(url)

@checkout_bp.route("/order-confirmation/<session_id>")
def confirmation(session_id):
    from models import Order
    order = Order.query.filter_by(stripe_session_id=session_id).first()
    return render_template("pages/order_confirmation.html", order=order)

@checkout_bp.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    from services.checkout_service import handle_webhook
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    result, code = handle_webhook(payload, sig)
    return result, code
