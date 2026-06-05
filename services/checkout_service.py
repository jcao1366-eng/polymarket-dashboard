import stripe
from flask import current_app
from services.cart_service import get_cart, clear_cart
from models import Order, OrderItem, db

def create_checkout_session(email, currency="USD"):
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    cart = get_cart()
    if not cart:
        return None, "Cart is empty"

    site_url = current_app.config["SITE_URL"]
    line_items = []
    for item in cart:
        p = item.product
        if not p:
            continue
        line_items.append({
            "price_data": {
                "currency": currency.lower(),
                "unit_amount": int(p.base_price * 100),
                "product_data": {"name": p.name, "images": [p.image_url] if p.image_url else []},
            },
            "quantity": item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url=f"{site_url}/order-confirmation/{{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{site_url}/cart",
        customer_email=email,
        metadata={"currency": currency},
    )
    return session.url, None

def handle_webhook(payload, sig_header):
    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
    webhook_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        _create_order(sess)
    return "OK", 200

def _create_order(sess):
    sid = sess.get("client_reference_id") or sess["id"]
    order = Order(
        order_number=f"ORD-{__import__('time').time():.0f}",
        stripe_session_id=sess["id"],
        email=sess.get("customer_details", {}).get("email", ""),
        status="paid",
        currency=sess.get("metadata", {}).get("currency", "USD"),
        total=sess["amount_total"] / 100,
    )
    db.session.add(order)
    db.session.commit()
