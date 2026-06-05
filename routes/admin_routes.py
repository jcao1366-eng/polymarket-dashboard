from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from services.admin_service import verify_admin, get_orders, get_all_products, update_order_status, get_product, create_product, update_product, delete_product, create_category, delete_category
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
    from models import Product, Order
    total_products = Product.query.count()
    total_orders = Order.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", total_products=total_products, total_orders=total_orders, recent_orders=recent_orders)

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
    prods = get_all_products()
    categories = get_categories()
    return render_template("admin/products.html", products=prods, categories=categories)

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
    return render_template("admin/product_form.html", categories=categories, product=None)

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
    return render_template("admin/product_form.html", categories=categories, product=p)

@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def remove_product(product_id):
    delete_product(product_id)
    flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))

@admin_bp.route("/categories")
@admin_required
def categories():
    cats = get_categories()
    return render_template("admin/categories.html", categories=cats)

@admin_bp.route("/categories/new", methods=["POST"])
@admin_required
def new_category():
    create_category(request.form.to_dict())
    flash("Category created!", "success")
    return redirect(url_for("admin.categories"))

@admin_bp.route("/categories/<int:cat_id>/delete", methods=["POST"])
@admin_required
def remove_category(cat_id):
    delete_category(cat_id)
    flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))
