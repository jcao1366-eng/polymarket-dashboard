from flask import Blueprint, render_template
from services.product_service import get_featured_products, get_categories

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    featured = get_featured_products(8)
    categories = get_categories()
    return render_template("pages/home.html", featured=featured, categories=categories)

@main_bp.route("/about")
def about():
    return render_template("pages/about.html")

@main_bp.route("/contact")
def contact():
    return render_template("pages/contact.html")

@main_bp.route("/privacy")
def privacy():
    return render_template("legal/privacy.html")

@main_bp.route("/terms")
def terms():
    return render_template("legal/terms.html")

@main_bp.route("/refund-policy")
def refund_policy():
    return render_template("legal/refund_policy.html")

@main_bp.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

@main_bp.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500
