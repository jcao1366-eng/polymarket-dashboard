from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.admin_service import verify_admin, get_orders, get_all_products, update_order_status

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if verify_admin(request.form.get("username", ""), request.form.get("password", "")):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials")
    return render_template("admin/login.html")

@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))

@admin_bp.route("/")
@admin_required
def dashboard():
    orders = get_orders()
    products = get_all_products()
    return render_template("admin/dashboard.html", orders=orders, products=products)

@admin_bp.route("/orders")
@admin_required
def orders():
    page = request.args.get("page", 1, type=int)
    orders = get_orders(page=page)
    return render_template("admin/orders.html", orders=orders)

@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def update_status(order_id):
    status = request.form.get("status", "pending")
    update_order_status(order_id, status)
    return redirect(url_for("admin.orders"))

@admin_bp.route("/products")
@admin_required
def products():
    products = get_all_products()
    return render_template("admin/products.html", products=products)
