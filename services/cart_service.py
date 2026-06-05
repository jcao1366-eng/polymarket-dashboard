from models import Product, ProductVariant, CartItem, db
from flask import session

def get_session_id():
    if "cart_sid" not in session:
        session["cart_sid"] = session.get("cart_sid") or __import__("uuid").uuid4().hex[:16]
    return session["cart_sid"]

def get_cart():
    sid = get_session_id()
    return CartItem.query.filter_by(session_id=sid).all()

def get_cart_count():
    sid = get_session_id()
    return sum(c.quantity for c in CartItem.query.filter_by(session_id=sid).all())

def get_cart_total(currency="USD"):
    from services.currency_service import convert
    items = get_cart()
    total_usd = sum(c.product.base_price * c.quantity for c in items if c.product)
    return convert(total_usd, "USD", currency)

def add_to_cart(product_id, variant_id=None, quantity=1):
    sid = get_session_id()
    existing = CartItem.query.filter_by(session_id=sid, product_id=product_id, variant_id=variant_id).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(session_id=sid, product_id=product_id, variant_id=variant_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()

def update_cart_item(item_id, quantity):
    item = CartItem.query.get_or_404(item_id)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()

def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

def clear_cart():
    sid = get_session_id()
    CartItem.query.filter_by(session_id=sid).delete()
    db.session.commit()
