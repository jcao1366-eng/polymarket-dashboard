from models import Product, Order, db
from werkzeug.security import check_password_hash
from flask import current_app

def verify_admin(username, password):
    return (username == current_app.config["ADMIN_USERNAME"]
            and password == current_app.config["ADMIN_PASSWORD"])

def get_orders(page=1, per_page=20):
    return Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

def get_all_products():
    return Product.query.order_by(Product.created_at.desc()).all()

def update_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    return order
