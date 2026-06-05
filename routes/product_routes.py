from flask import Blueprint, render_template, request
from services.product_service import get_products, get_product_by_slug, get_categories

product_bp = Blueprint("product", __name__)

@product_bp.route("/products")
def product_list():
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "newest")
    search = request.args.get("q", "")
    category_slug = request.args.get("category", "")
    products = get_products(page=page, sort=sort, search=search, category_slug=category_slug)
    categories = get_categories()
    return render_template("pages/product_list.html", products=products, categories=categories, sort=sort, search=search, category_slug=category_slug)

@product_bp.route("/products/<slug>")
def product_detail(slug):
    product = get_product_by_slug(slug)
    return render_template("pages/product_detail.html", product=product)

@product_bp.route("/categories/<slug>")
def category_products(slug):
    products = get_products(category_slug=slug)
    categories = get_categories()
    cat = next((c for c in categories if c.slug == slug), None)
    return render_template("pages/product_list.html", products=products, categories=categories, category_slug=slug, category_name=cat.name if cat else "")
