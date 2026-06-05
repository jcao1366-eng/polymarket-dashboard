"""Add admin product CRUD + auto-seed on startup + improved detail page."""
import os

BASE = r"C:\Users\34387\WorkBuddy\Claw\polymarket-bot"

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  wrote {path}")

def main():
    print("=== Updating Admin + Detail + Auto-seed ===\n")

    # ─── app.py: add auto-seed ───
    w("app.py", """\
import os
import logging
from flask import Flask
from config import Config
from models import db

log = logging.getLogger(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from routes.main import main_bp
    from routes.product_routes import product_bp
    from routes.cart_routes import cart_bp
    from routes.checkout_routes import checkout_bp
    from routes.api_routes import api_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()
        _auto_seed(app)

    return app

def _auto_seed(app):
    \"\"\"Auto-seed products if the database is empty.\"\"\"
    from models import Product, Category, ProductVariant
    if Product.query.first() is not None:
        return
    log.info("Database empty, seeding sample data...")
    cats = [
        Category(name="Home Decor", slug="home-decor", description="Unique home decoration pieces", sort_order=1, image_url="https://placehold.co/600x400/f5f3ff/7C3AED?text=Home+Decor"),
        Category(name="Art Prints", slug="art-prints", description="Museum-quality art prints and posters", sort_order=2, image_url="https://placehold.co/600x400/ede9fe/7C3AED?text=Art+Prints"),
        Category(name="Stationery", slug="stationery", description="Creative stationery and desk accessories", sort_order=3, image_url="https://placehold.co/600x400/ddd6fe/7C3AED?text=Stationery"),
        Category(name="Accessories", slug="accessories", description="Unique fashion accessories and jewelry", sort_order=4, image_url="https://placehold.co/600x400/c4b5fd/7C3AED?text=Accessories"),
    ]
    for c in cats:
        db.session.add(c)
    db.session.flush()

    products = [
        ("Abstract Canvas Wall Art", "abstract-canvas-wall-art", 39.99, 79.99,
         "Hand-painted abstract canvas art. Textured brush strokes create depth and movement. Perfect for modern living spaces.\n\n- Size: 24x36 inches\n- Material: Premium cotton canvas\n- Comes with hanging hardware\n- UV-resistant ink",
         "home-decor", True, ["Color", "Style"], ["Navy/Abstract", "Terracotta/Geometric", "Sage/Minimal"]),
        ("Minimalist Line Art Print", "minimalist-line-art-print", 24.99, 44.99,
         "Elegant continuous line art print. Modern and sophisticated wall decoration.\n\n- Size: 16x20 inches\n- Printed on 250gsm archival paper\n- Mat board included\n- Fits standard frames",
         "art-prints", True, ["Style"], ["Face Profile", "Figure", "Flower"]),
        ("Ceramic Vase Set", "ceramic-vase-set", 34.99, 59.99,
         "Set of 3 handmade ceramic vases in gradient tones. Each piece is unique.\n\n- Set of 3 (small, medium, large)\n- Material: Premium stoneware\n- Food-safe glaze\n- Waterproof interior",
         "home-decor", True, ["Color"], ["Ocean Blue", "Dusty Rose", "Forest Green"]),
        ("Creative Desk Organizer", "creative-desk-organizer", 28.99, 49.99,
         "Modular desk organizer with geometric design. Keep your workspace tidy in style.\n\n- 5 compartments\n- Material: Bamboo + Concrete\n- Pen holder + phone slot\n- Cable management built-in",
         "stationery", True, ["Color"], ["Charcoal", "White Marble", "Wood Grain"]),
        ("Geometric Statement Necklace", "geometric-statement-necklace", 19.99, 34.99,
         "Bold geometric necklace. Gold-plated brass with adjustable chain.\n\n- Chain length: 16-20 inches adjustable\n- Material: Gold-plated brass\n- Hypoallergenic\n- Gift box included",
         "accessories", True, ["Finish"], ["Gold", "Rose Gold", "Silver"]),
        ("Watercolor Art Book Set", "watercolor-art-book-set", 22.99, 38.99,
         "Set of 2 beautifully illustrated art books. Watercolor techniques and inspiration.\n\n- Hardback, 128 pages each\n- Full-color illustrations\n- English edition\n- Perfect gift for art lovers",
         "art-prints", True, ["Binding"], ["Hardcover", "Softcover"]),
        ("Marble Coaster Set", "marble-coaster-set", 18.99, 32.99,
         "Set of 4 natural marble coasters with gold-edge detail. Cork-backed.\n\n- 4x4 inches each\n- Natural marble (varies slightly)\n- Cork backing protects surfaces\n- Elegant gift packaging",
         "home-decor", True, ["Shape"], ["Square", "Round"]),
        ("Creative Washi Tape Collection", "washi-tape-collection", 12.99, 22.99,
         "Set of 12 decorative washi tapes. Unique patterns designed by independent artists.\n\n- 12 rolls, 10mm wide\n- 5 meters per roll\n- Washi paper, repositionable\n- Patterns: geometric, floral, abstract",
         "stationery", True, [], []),
        ("Brass Wire Sculpture", "brass-wire-sculpture", 44.99, 79.99,
         "Hand-bent brass wire sculpture. Abstract organic form adds artistic flair to any shelf.\n\n- Height: 12 inches\n- Material: Solid brass, lacquered finish\n- Base: Black marble\n- No two exactly alike",
         "home-decor", True, ["Form"], ["Tree", "Figure", "Abstract"]),
        ("Creative Pendant Light", "creative-pendant-light", 54.99, 89.99,
         "Designer pendant light with woven rattan shade. Warm ambient lighting.\n\n- Shade diameter: 14 inches\n- Cable length: adjustable up to 59 inches\n- Bulb: E26, max 60W (not included)\n- UL listed",
         "home-decor", True, ["Color"], ["Natural Rattan", "Black Rattan", "White Rattan"]),
        ("Hand-lettered Quote Print", "hand-lettered-quote-print", 16.99, 29.99,
         "Inspirational hand-lettered quote print. Motivational wall art for home or office.\n\n- Size: 11x14 inches\n- Printed on premium matte paper\n- Frame not included\n- Multiple quotes available",
         "art-prints", True, ["Quote"], ["Dream Big", "Stay Curious", "Be Bold"]),
        ("Leather Bookmark Set", "leather-bookmark-set", 14.99, 24.99,
         "Set of 3 genuine leather bookmarks with embossed designs. Perfect for book lovers.\n\n- 3 bookmarks with different patterns\n- Genuine top-grain leather\n- Gift box included\n- Tassel detail",
         "stationery", True, ["Color"], ["Brown", "Black", "Burgundy"]),
    ]
    for name, slug, price, compare, desc, cat_slug, featured, opt_names, opt_values in products:
        cat = next((c for c in cats if c.slug == cat_slug), None)
        p = Product(
            name=name, slug=slug, base_price=price, compare_price=compare,
            description=desc, is_featured=featured,
            image_url=f"https://placehold.co/800x800/f5f3ff/7C3AED?text={slug.replace('-', '+')[:20]}",
            images=[
                f"https://placehold.co/800x800/f5f3ff/7C3AED?text={slug.replace('-', '+')[:15]}+2",
                f"https://placehold.co/800x800/ede9fe/7C3AED?text={slug.replace('-', '+')[:15]}+3",
            ],
        )
        if cat:
            p.categories.append(cat)
        # Add variants
        if opt_names and opt_values:
            for vals in opt_values:
                opts = dict(zip(opt_names, vals.split("/")))
                p.variants.append(ProductVariant(
                    sku=f"SKU-{slug[:6].upper()}-{vals[:4].lower()}",
                    options=opts, stock=50
                ))
        else:
            p.variants.append(ProductVariant(sku=f"SKU-{slug[:8].upper()}", options={"Default": "One Size"}, stock=100))
        db.session.add(p)
    db.session.commit()
    log.info(f"Seeded {len(products)} products across {len(cats)} categories.")

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
""")

    # ─── admin_service.py: add product CRUD ───
    w("services/admin_service.py", """\
from models import Product, ProductVariant, Category, Order, db
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

def get_product(product_id):
    return Product.query.get_or_404(product_id)

def create_product(data):
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', data.get("slug") or data.get("name", "").lower()).strip("-")
    # Ensure unique slug
    base_slug = slug
    counter = 1
    while Product.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    p = Product(
        name=data["name"], slug=slug,
        base_price=float(data.get("base_price", 0)),
        compare_price=float(data.get("compare_price", 0)) or None,
        cost_price=float(data.get("cost_price", 0)) or None,
        description=data.get("description", ""),
        description_en=data.get("description_en", ""),
        supplier_url=data.get("supplier_url", ""),
        image_url=data.get("image_url", ""),
        images=_parse_images(data.get("images", "")),
        is_active=data.get("is_active", True),
        is_featured=data.get("is_featured", False),
        seo_title=data.get("seo_title", ""),
        seo_description=data.get("seo_description", ""),
    )
    # Categories
    if data.get("categories"):
        for cid in data["categories"]:
            cat = Category.query.get(int(cid))
            if cat:
                p.categories.append(cat)
    db.session.add(p)
    db.session.flush()
    # Variants
    _save_variants(p, data)
    db.session.commit()
    return p

def update_product(product_id, data):
    p = get_product(product_id)
    import re
    if "name" in data and data["name"]:
        p.name = data["name"]
        if data.get("slug"):
            slug = re.sub(r'[^a-z0-9]+', '-', data["slug"].lower()).strip("-")
            p.slug = slug
    if "base_price" in data:
        p.base_price = float(data["base_price"])
    if "compare_price" in data:
        p.compare_price = float(data["compare_price"]) if data["compare_price"] else None
    if "cost_price" in data:
        p.cost_price = float(data["cost_price"]) if data["cost_price"] else None
    if "description" in data:
        p.description = data["description"]
    if "description_en" in data:
        p.description_en = data["description_en"]
    if "supplier_url" in data:
        p.supplier_url = data["supplier_url"]
    if "image_url" in data:
        p.image_url = data["image_url"]
    if "images" in data:
        p.images = _parse_images(data["images"])
    if "is_active" in data:
        p.is_active = data["is_active"]
    if "is_featured" in data:
        p.is_featured = data["is_featured"]
    if "seo_title" in data:
        p.seo_title = data["seo_title"]
    if "seo_description" in data:
        p.seo_description = data["seo_description"]
    if "categories" in data:
        p.categories.clear()
        for cid in data["categories"]:
            cat = Category.query.get(int(cid))
            if cat:
                p.categories.append(cat)
    _save_variants(p, data)
    db.session.commit()
    return p

def delete_product(product_id):
    p = get_product(product_id)
    p.variants.delete()
    db.session.delete(p)
    db.session.commit()

def create_category(data):
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', data.get("slug") or data.get("name", "").lower()).strip("-")
    cat = Category(
        name=data["name"], slug=slug,
        description=data.get("description", ""),
        image_url=data.get("image_url", ""),
        sort_order=int(data.get("sort_order", 0)),
    )
    db.session.add(cat)
    db.session.commit()
    return cat

def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()

def _parse_images(images_str):
    if not images_str:
        return []
    return [url.strip() for url in images_str.strip().split("\\n") if url.strip()]

def _save_variants(product, data):
    # Clear existing if variant_data provided
    if "variant_options" in data:
        ProductVariant.query.filter_by(product_id=product.id).delete()
        options = data["variant_options"]  # list of dicts: [{name, value, sku, stock, price_modifier}]
        for opt in options:
            if opt.get("value"):
                v = ProductVariant(
                    product_id=product.id,
                    sku=opt.get("sku", ""),
                    options={opt.get("name", "Default"): opt["value"]},
                    stock=int(opt.get("stock", 999)),
                    price_modifier=float(opt.get("price_modifier", 0)) or 0,
                )
                db.session.add(v)
""")

    # ─── admin_routes.py: add CRUD endpoints ───
    w("routes/admin_routes.py", """\
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
""")

    # ─── admin/product_form.html: full product editor ───
    w("templates/admin/product_form.html", """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ 'Edit' if product else 'New' }} Product - Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .field { margin-bottom: 1rem; }
        .field label { display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.25rem; }
        .field input, .field textarea, .field select { width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #e5e7eb; border-radius: 0.5rem; font-size: 0.875rem; }
        .field input:focus, .field textarea:focus, .field select:focus { outline: none; box-shadow: 0 0 0 3px rgba(124,58,237,0.15); border-color: #7C3AED; }
        .field .hint { font-size: 0.75rem; color: #9ca3af; margin-top: 0.25rem; }
        .field textarea { min-height: 120px; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-gray-900 text-white px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-6">
            <a href="{{ url_for('admin.dashboard') }}" class="font-bold hover:text-gray-300">&larr; Admin</a>
            <span>{{ 'Edit Product' if product else 'New Product' }}</span>
        </div>
        <a href="{{ url_for('admin.products') }}" class="text-sm hover:text-gray-300">Back to Products</a>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="max-w-4xl mx-auto mt-4">
        {% for category, message in messages %}
        <div class="px-4 py-3 rounded-lg mb-2 text-sm {% if category == 'success' %}bg-green-50 text-green-700{% else %}bg-red-50 text-red-700{% endif %}">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}
    {% endwith %}

    <div class="max-w-4xl mx-auto px-6 py-8">
        <form method="post">
            <!-- Basic Info -->
            <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
                <h2 class="text-lg font-bold text-gray-900 mb-4">Basic Information</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="field">
                        <label>Product Name *</label>
                        <input type="text" name="name" required value="{{ product.name if product else '' }}" placeholder="e.g. Abstract Canvas Wall Art">
                    </div>
                    <div class="field">
                        <label>Slug (URL)</label>
                        <input type="text" name="slug" value="{{ product.slug if product else '' }}" placeholder="auto-generated-from-name">
                        <div class="hint">Leave blank to auto-generate from name</div>
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="field">
                        <label>Selling Price ($) *</label>
                        <input type="number" step="0.01" min="0" name="base_price" required value="{{ '%.2f'|format(product.base_price) if product else '' }}">
                    </div>
                    <div class="field">
                        <label>Compare at Price ($)</label>
                        <input type="number" step="0.01" min="0" name="compare_price" value="{{ '%.2f'|format(product.compare_price) if product and product.compare_price else '' }}">
                        <div class="hint">Original price for discount display</div>
                    </div>
                    <div class="field">
                        <label>Cost Price ($)</label>
                        <input type="number" step="0.01" min="0" name="cost_price" value="{{ '%.2f'|format(product.cost_price) if product and product.cost_price else '' }}">
                        <div class="hint">Your cost (not shown to customers)</div>
                    </div>
                </div>
                <div class="field">
                    <label>Categories</label>
                    <div class="flex flex-wrap gap-3 mt-1">
                        {% for cat in categories %}
                        <label class="flex items-center gap-1.5 text-sm text-gray-700">
                            <input type="checkbox" name="categories" value="{{ cat.id }}" {% if product and cat in product.categories %}checked{% endif %}>
                            {{ cat.name }}
                        </label>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Description -->
            <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
                <h2 class="text-lg font-bold text-gray-900 mb-4">Description</h2>
                <div class="field">
                    <label>Description (Chinese)</label>
                    <textarea name="description" rows="6">{{ product.description if product else '' }}</textarea>
                    <div class="hint">Main description. Use blank lines for paragraphs.</div>
                </div>
                <div class="field">
                    <label>Description (English)</label>
                    <textarea name="description_en" rows="6">{{ product.description_en if product else '' }}</textarea>
                </div>
            </div>

            <!-- Images -->
            <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
                <h2 class="text-lg font-bold text-gray-900 mb-4">Images</h2>
                <div class="field">
                    <label>Main Image URL *</label>
                    <input type="url" name="image_url" value="{{ product.image_url if product else '' }}" placeholder="https://example.com/image.jpg">
                </div>
                <div class="field">
                    <label>Additional Images</label>
                    <textarea name="images" rows="4" placeholder="One URL per line">{{ '\\n'.join(product.images) if product and product.images else '' }}</textarea>
                    <div class="hint">One image URL per line. These show in the product gallery.</div>
                </div>
                {% if product and product.image_url %}
                <div class="mt-4">
                    <p class="text-sm text-gray-500 mb-2">Preview:</p>
                    <div class="grid grid-cols-4 gap-2">
                        <img src="{{ product.image_url }}" alt="" class="w-full aspect-square object-cover rounded-lg border">
                        {% for img in (product.images or [])[:3] %}
                        <img src="{{ img }}" alt="" class="w-full aspect-square object-cover rounded-lg border">
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
            </div>

            <!-- Supplier & SEO -->
            <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
                <h2 class="text-lg font-bold text-gray-900 mb-4">Supplier &amp; SEO</h2>
                <div class="field">
                    <label>Supplier URL (1688/Taobao)</label>
                    <input type="url" name="supplier_url" value="{{ product.supplier_url if product else '' }}" placeholder="https://detail.1688.com/...">
                    <div class="hint">Link to your supplier for easy reordering</div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="field">
                        <label>SEO Title</label>
                        <input type="text" name="seo_title" value="{{ product.seo_title if product else '' }}" placeholder="Custom title for search engines">
                    </div>
                    <div class="field">
                        <label>SEO Description</label>
                        <input type="text" name="seo_description" value="{{ product.seo_description if product else '' }}" placeholder="Meta description (max 160 chars)">
                    </div>
                </div>
            </div>

            <!-- Status -->
            <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
                <h2 class="text-lg font-bold text-gray-900 mb-4">Status</h2>
                <div class="flex items-center gap-6">
                    <label class="flex items-center gap-2 text-sm text-gray-700">
                        <input type="checkbox" name="is_active" {% if not product or product.is_active %}checked{% endif %}>
                        Active (visible in store)
                    </label>
                    <label class="flex items-center gap-2 text-sm text-gray-700">
                        <input type="checkbox" name="is_featured" {% if product and product.is_featured %}checked{% endif %}>
                        Featured (show on homepage)
                    </label>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-4">
                <button type="submit" class="px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition">
                    {{ 'Save Changes' if product else 'Create Product' }}
                </button>
                <a href="{{ url_for('admin.products') }}" class="px-6 py-3 text-gray-600 hover:text-gray-800">Cancel</a>
                {% if product %}
                <form method="post" action="{{ url_for('admin.remove_product', product_id=product.id) }}" class="ml-auto" onsubmit="return confirm('Delete this product permanently?')">
                    <button type="submit" class="px-4 py-3 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition">Delete Product</button>
                </form>
                {% endif %}
            </div>
        </form>
    </div>
</body>
</html>
""")

    # ─── admin/products.html: enhanced product list ───
    w("templates/admin/products.html", """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products - Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-gray-900 text-white px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-6">
            <a href="{{ url_for('admin.dashboard') }}" class="font-bold hover:text-gray-300">&larr; Admin</a>
            <span>Products</span>
        </div>
        <div class="flex gap-4">
            <a href="{{ url_for('admin.categories') }}" class="hover:text-gray-300">Categories</a>
            <a href="{{ url_for('admin.logout') }}" class="hover:text-gray-300">Logout</a>
        </div>
    </nav>
    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="max-w-7xl mx-auto mt-4 px-6">
        {% for category, message in messages %}
        <div class="px-4 py-3 rounded-lg mb-2 text-sm {% if category == 'success' %}bg-green-50 text-green-700{% else %}bg-red-50 text-red-700{% endif %}">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}
    {% endwith %}
    <div class="max-w-7xl mx-auto px-6 py-8">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900">{{ products|length }} Products</h1>
            <a href="{{ url_for('admin.new_product') }}" class="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition">+ New Product</a>
        </div>
        <div class="bg-white rounded-xl shadow-sm overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Image</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Featured</th>
                        <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                {% for p in products %}
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-3">
                        <img src="{{ p.image_url or 'https://placehold.co/48x48/e9d5ff/7C3AED' }}" alt="" class="w-12 h-12 object-cover rounded-lg">
                    </td>
                    <td class="px-4 py-3">
                        <a href="{{ url_for('product.product_detail', slug=p.slug) }}" target="_blank" class="text-sm font-medium text-gray-900 hover:text-indigo-600">{{ p.name }}</a>
                        <div class="text-xs text-gray-400 mt-0.5">{{ p.slug }}</div>
                    </td>
                    <td class="px-4 py-3">
                        <span class="text-sm font-medium">${{ '%.2f'|format(p.base_price) }}</span>
                        {% if p.compare_price and p.compare_price > p.base_price %}
                        <span class="text-xs text-gray-400 line-through ml-1">${{ '%.2f'|format(p.compare_price) }}</span>
                        {% endif %}
                    </td>
                    <td class="px-4 py-3">
                        <span class="px-2 py-1 text-xs font-medium rounded-full {% if p.is_active %}bg-green-100 text-green-700{% else %}bg-gray-100 text-gray-500{% endif %}">{% if p.is_active %}Active{% else %}Draft{% endif %}</span>
                    </td>
                    <td class="px-4 py-3">
                        {% if p.is_featured %}<span class="text-yellow-500">&#9733;</span>{% else %}<span class="text-gray-300">&#9734;</span>{% endif %}
                    </td>
                    <td class="px-4 py-3 text-right">
                        <a href="{{ url_for('admin.edit_product', product_id=p.id) }}" class="text-sm text-indigo-600 hover:text-indigo-800 mr-3">Edit</a>
                        <form method="post" action="{{ url_for('admin.remove_product', product_id=p.id) }}" class="inline" onsubmit="return confirm('Delete {{ p.name }}?')">
                            <button type="submit" class="text-sm text-red-500 hover:text-red-700">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
            {% if not products %}
            <div class="text-center py-12 text-gray-400">
                <p>No products yet. <a href="{{ url_for('admin.new_product') }}" class="text-indigo-600 hover:underline">Create your first product</a></p>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
""")

    # ─── admin/categories.html: category management ───
    w("templates/admin/categories.html", """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Categories - Admin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-gray-900 text-white px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-6">
            <a href="{{ url_for('admin.dashboard') }}" class="font-bold hover:text-gray-300">&larr; Admin</a>
            <span>Categories</span>
        </div>
        <a href="{{ url_for('admin.logout') }}" class="hover:text-gray-300">Logout</a>
    </nav>
    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="max-w-4xl mx-auto mt-4 px-6">
        {% for category, message in messages %}
        <div class="px-4 py-3 rounded-lg mb-2 text-sm {% if category == 'success' %}bg-green-50 text-green-700{% else %}bg-red-50 text-red-700{% endif %}">{{ message }}</div>
        {% endfor %}
    </div>
    {% endif %}
    {% endwith %}
    <div class="max-w-4xl mx-auto px-6 py-8">
        <h1 class="text-2xl font-bold mb-6">Categories ({{ categories|length }})</h1>
        <!-- Add new category -->
        <div class="bg-white rounded-xl p-6 shadow-sm mb-6">
            <h2 class="text-sm font-semibold text-gray-700 mb-4">Add New Category</h2>
            <form method="post" action="{{ url_for('admin.new_category') }}" class="flex gap-3">
                <input type="text" name="name" required placeholder="Category name" class="flex-1 px-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <input type="text" name="slug" placeholder="slug (auto)" class="w-40 px-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <button type="submit" class="px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700">Add</button>
            </form>
        </div>
        <!-- Category list -->
        <div class="bg-white rounded-xl shadow-sm overflow-hidden">
            <table class="w-full">
                <thead class="bg-gray-50"><tr><th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th><th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Slug</th><th class="px-6 py-3 text-right text-sm font-medium text-gray-500">Actions</th></tr></thead>
                <tbody class="divide-y divide-gray-100">
                {% for cat in categories %}
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ cat.name }}</td>
                    <td class="px-6 py-4 text-sm text-gray-500 font-mono">{{ cat.slug }}</td>
                    <td class="px-6 py-4 text-right">
                        <form method="post" action="{{ url_for('admin.remove_category', cat_id=cat.id) }}" onsubmit="return confirm('Delete {{ cat.name }}?')">
                            <button type="submit" class="text-sm text-red-500 hover:text-red-700">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
""")

    # ─── admin/dashboard.html: improved with stats ───
    w("templates/admin/dashboard.html", """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-gray-900 text-white px-6 py-4 flex items-center justify-between">
        <span class="font-bold">Creative Finds Admin</span>
        <div class="flex gap-4 text-sm">
            <a href="{{ url_for('admin.products') }}" class="hover:text-gray-300">Products</a>
            <a href="{{ url_for('admin.categories') }}" class="hover:text-gray-300">Categories</a>
            <a href="{{ url_for('admin.orders') }}" class="hover:text-gray-300">Orders</a>
            <a href="{{ url_for('admin.logout') }}" class="hover:text-gray-300">Logout</a>
        </div>
    </nav>
    <div class="max-w-7xl mx-auto px-6 py-8">
        <h1 class="text-2xl font-bold mb-8">Dashboard</h1>
        <!-- Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-xl p-6 shadow-sm">
                <div class="text-sm text-gray-500">Total Products</div>
                <div class="text-3xl font-bold mt-1">{{ total_products }}</div>
                <a href="{{ url_for('admin.new_product') }}" class="text-sm text-indigo-600 hover:text-indigo-800 mt-2 inline-block">+ Add Product</a>
            </div>
            <div class="bg-white rounded-xl p-6 shadow-sm">
                <div class="text-sm text-gray-500">Total Orders</div>
                <div class="text-3xl font-bold mt-1">{{ total_orders }}</div>
                <a href="{{ url_for('admin.orders') }}" class="text-sm text-indigo-600 hover:text-indigo-800 mt-2 inline-block">View Orders</a>
            </div>
            <div class="bg-white rounded-xl p-6 shadow-sm">
                <div class="text-sm text-gray-500">Quick Actions</div>
                <div class="mt-3 flex flex-col gap-2">
                    <a href="{{ url_for('admin.new_product') }}" class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 text-center">New Product</a>
                    <a href="https://polymarket-dashboard-xq1a.onrender.com" target="_blank" class="px-4 py-2 border border-gray-200 text-sm rounded-lg hover:bg-gray-50 text-center">View Store</a>
                </div>
            </div>
        </div>
        <!-- Recent Orders -->
        {% if recent_orders %}
        <h2 class="text-lg font-bold mb-4">Recent Orders</h2>
        <div class="bg-white rounded-xl shadow-sm overflow-hidden">
            <table class="w-full">
                <thead class="bg-gray-50"><tr><th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Order</th><th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Email</th><th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Total</th><th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Status</th></tr></thead>
                <tbody class="divide-y divide-gray-100">
                {% for order in recent_orders %}
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 font-mono text-sm">{{ order.order_number }}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">{{ order.email }}</td>
                    <td class="px-6 py-4 font-medium">${{ '%.2f'|format(order.total) }}</td>
                    <td class="px-6 py-4"><span class="px-2 py-1 text-xs font-medium rounded-full {% if order.status == 'paid' %}bg-green-100 text-green-700{% elif order.status == 'shipped' %}bg-blue-100 text-blue-700{% else %}bg-yellow-100 text-yellow-700{% endif %}">{{ order.status }}</span></td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>
</body>
</html>
""")

    # ─── Improved product_detail.html ───
    w("templates/pages/product_detail.html", """\
{% extends "base.html" %}
{% block title %}{{ product.name }} | {{ config.STORE_NAME }}{% endblock %}
{% block meta_desc %}{{ product.description[:160] if product.description else 'Buy ' + product.name + ' at ' + config.STORE_NAME }}{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Breadcrumb -->
    <nav class="text-sm text-gray-500 mb-6 flex items-center gap-1">
        <a href="{{ url_for('main.home') }}" class="hover:text-primary-600">Home</a>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        <a href="{{ url_for('product.product_list') }}" class="hover:text-primary-600">Products</a>
        {% if product.categories and product.categories[0] %}
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        <a href="{{ url_for('product.category_products', slug=product.categories[0].slug) }}" class="hover:text-primary-600">{{ product.categories[0].name }}</a>
        {% endif %}
    </nav>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16">
        <!-- Image Gallery -->
        <div class="space-y-4">
            <div class="aspect-square rounded-2xl overflow-hidden bg-gray-50 shadow-sm">
                <img id="main-image" src="{{ product.image_url or 'https://placehold.co/800x800/f5f3ff/7C3AED?text=' + product.name[:10] }}" alt="{{ product.name }}" class="w-full h-full object-cover transition-all duration-300">
            </div>
            {% set all_images = [product.image_url] + (product.images or []) %}
            {% if all_images|length > 1 %}
            <div class="grid grid-cols-5 gap-3">
                {% for img in all_images[:5] %}
                <button onclick="switchImage('{{ img }}', this)" class="aspect-square rounded-xl overflow-hidden border-2 {% if loop.first %}border-primary-500{% else %}border-transparent{% endif %} hover:border-primary-300 transition-all">
                    <img src="{{ img }}" alt="" class="w-full h-full object-cover">
                </button>
                {% endfor %}
            </div>
            {% endif %}
        </div>

        <!-- Product Info -->
        <div>
            <!-- Category tags -->
            {% if product.categories %}
            <div class="flex gap-2 mb-3">
                {% for cat in product.categories %}
                <a href="{{ url_for('product.category_products', slug=cat.slug) }}" class="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full hover:bg-primary-50 hover:text-primary-600 transition">{{ cat.name }}</a>
                {% endfor %}
            </div>
            {% endif %}

            <h1 class="text-3xl md:text-4xl font-bold text-gray-900 leading-tight">{{ product.name }}</h1>

            <!-- Price -->
            <div class="mt-4 flex items-baseline gap-3">
                <span class="text-3xl font-bold text-gray-900">${{ '%.2f'|format(product.base_price) }}</span>
                {% if product.compare_price and product.compare_price > product.base_price %}
                <span class="text-lg text-gray-400 line-through">${{ '%.2f'|format(product.compare_price) }}</span>
                <span class="px-2.5 py-1 text-sm font-semibold text-white bg-red-500 rounded-full">-{{ product.discount_pct }}%</span>
                {% endif %}
            </div>

            <!-- Description -->
            <div class="mt-6 text-gray-600 leading-relaxed">
                {{ product.description|replace('\n', '<br>')|safe if product.description else '' }}
            </div>

            <!-- Variants -->
            {% if product.variants and product.variants.count() > 0 %}
            {% set unique_opt_names = [] %}
            {% for v in product.variants %}
                {% for key in v.options.keys() %}
                    {% if key not in unique_opt_names %}
                        {% if unique_opt_names.append(key) %}{% endif %}
                    {% endif %}
                {% endfor %}
            {% endfor %}
            {% for opt_name in unique_opt_names %}
            <div class="mt-6">
                <h3 class="text-sm font-semibold text-gray-900 mb-3">{{ opt_name }}</h3>
                <div class="flex flex-wrap gap-2">
                    {% set seen = [] %}
                    {% for v in product.variants %}
                        {% if v.options.get(opt_name) and v.options[opt_name] not in seen %}
                            {% if seen.append(v.options[opt_name]) %}{% endif %}
                            <button onclick="selectVariant(this)" class="variant-btn px-5 py-2.5 text-sm border-2 rounded-xl transition-all {% if loop.first %}border-primary-600 bg-primary-50 text-primary-700 font-medium{% else %}border-gray-200 hover:border-primary-300 text-gray-700{% endif %}" data-value="{{ v.options[opt_name] }}">
                                {{ v.options[opt_name] }}
                            </button>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
            {% endif %}

            <!-- Quantity + Add to Cart -->
            <div class="mt-8 flex items-center gap-4">
                <div class="flex items-center border border-gray-200 rounded-xl overflow-hidden">
                    <button onclick="updateQty(-1)" class="px-4 py-3 text-gray-600 hover:bg-gray-50 transition text-lg">-</button>
                    <input id="qty" type="number" value="1" min="1" class="w-14 text-center border-x border-gray-200 py-3 font-medium focus:outline-none text-gray-900">
                    <button onclick="updateQty(1)" class="px-4 py-3 text-gray-600 hover:bg-gray-50 transition text-lg">+</button>
                </div>
                <form action="{{ url_for('cart.add') }}" method="post" class="flex-1" id="add-to-cart-form">
                    <input type="hidden" name="product_id" value="{{ product.id }}">
                    <input type="hidden" name="quantity" id="add-qty" value="1">
                    <button type="submit" class="w-full py-3.5 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-500/25 active:scale-[0.98] flex items-center justify-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"></path></svg>
                        Add to Cart
                    </button>
                </form>
            </div>

            <!-- Trust badges -->
            <div class="mt-8 grid grid-cols-2 gap-3">
                <div class="flex items-center gap-2.5 bg-gray-50 rounded-xl px-4 py-3">
                    <svg class="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8"></path></svg>
                    <span class="text-xs text-gray-600">Free shipping over $50</span>
                </div>
                <div class="flex items-center gap-2.5 bg-gray-50 rounded-xl px-4 py-3">
                    <svg class="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                    <span class="text-xs text-gray-600">30-day returns</span>
                </div>
                <div class="flex items-center gap-2.5 bg-gray-50 rounded-xl px-4 py-3">
                    <svg class="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                    <span class="text-xs text-gray-600">Secure payment</span>
                </div>
                <div class="flex items-center gap-2.5 bg-gray-50 rounded-xl px-4 py-3">
                    <svg class="w-5 h-5 text-primary-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path></svg>
                    <span class="text-xs text-gray-600">Worldwide delivery</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function switchImage(url, btn) {
    document.getElementById('main-image').src = url;
    document.querySelectorAll('[onclick^="switchImage"]').forEach(b => b.classList.remove('border-primary-500'));
    btn.classList.add('border-primary-500');
}

function selectVariant(btn) {
    btn.closest('.flex').querySelectorAll('.variant-btn').forEach(b => {
        b.classList.remove('border-primary-600', 'bg-primary-50', 'text-primary-700', 'font-medium');
        b.classList.add('border-gray-200', 'text-gray-700');
    });
    btn.classList.remove('border-gray-200', 'text-gray-700');
    btn.classList.add('border-primary-600', 'bg-primary-50', 'text-primary-700', 'font-medium');
}

function updateQty(d) {
    const q = document.getElementById('qty');
    const n = Math.max(1, parseInt(q.value) + d);
    q.value = n;
    document.getElementById('add-qty').value = n;
}

// Intercept add-to-cart for toast
document.getElementById('add-to-cart-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const fd = new FormData(this);
    fetch(this.action, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('cart-badge');
            if (badge) { badge.textContent = data.count; badge.classList.remove('hidden'); badge.classList.add('bump'); setTimeout(() => badge.classList.remove('bump'), 300); }
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = 'Added to cart!';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        });
});
</script>
{% endblock %}
""")

    print("\n=== Done! Admin CRUD + auto-seed + detail page updated. ===")

if __name__ == "__main__":
    main()
