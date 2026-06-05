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
    """Auto-seed products if the database is empty."""
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
         "Hand-painted abstract canvas art. Textured brush strokes create depth and movement. Perfect for modern living spaces.\n- Size: 24x36 inches\n- Material: Premium cotton canvas\n- Comes with hanging hardware\n- UV-resistant ink",
         "home-decor", True, ["Color", "Style"], ["Navy/Abstract", "Terracotta/Geometric", "Sage/Minimal"]),
        ("Minimalist Line Art Print", "minimalist-line-art-print", 24.99, 44.99,
         "Elegant continuous line art print. Modern and sophisticated wall decoration.\n- Size: 16x20 inches\n- Printed on 250gsm archival paper\n- Mat board included\n- Fits standard frames",
         "art-prints", True, ["Style"], ["Face Profile", "Figure", "Flower"]),
        ("Ceramic Vase Set", "ceramic-vase-set", 34.99, 59.99,
         "Set of 3 handmade ceramic vases in gradient tones. Each piece is unique.\n- Set of 3 (small, medium, large)\n- Material: Premium stoneware\n- Food-safe glaze\n- Waterproof interior",
         "home-decor", True, ["Color"], ["Ocean Blue", "Dusty Rose", "Forest Green"]),
        ("Creative Desk Organizer", "creative-desk-organizer", 28.99, 49.99,
         "Modular desk organizer with geometric design. Keep your workspace tidy in style.\n- 5 compartments\n- Material: Bamboo + Concrete\n- Pen holder + phone slot\n- Cable management built-in",
         "stationery", True, ["Color"], ["Charcoal", "White Marble", "Wood Grain"]),
        ("Geometric Statement Necklace", "geometric-statement-necklace", 19.99, 34.99,
         "Bold geometric necklace. Gold-plated brass with adjustable chain.\n- Chain length: 16-20 inches adjustable\n- Material: Gold-plated brass\n- Hypoallergenic\n- Gift box included",
         "accessories", True, ["Finish"], ["Gold", "Rose Gold", "Silver"]),
        ("Watercolor Art Book Set", "watercolor-art-book-set", 22.99, 38.99,
         "Set of 2 beautifully illustrated art books. Watercolor techniques and inspiration.\n- Hardback, 128 pages each\n- Full-color illustrations\n- English edition\n- Perfect gift for art lovers",
         "art-prints", True, ["Binding"], ["Hardcover", "Softcover"]),
        ("Marble Coaster Set", "marble-coaster-set", 18.99, 32.99,
         "Set of 4 natural marble coasters with gold-edge detail. Cork-backed.\n- 4x4 inches each\n- Natural marble (varies slightly)\n- Cork backing protects surfaces\n- Elegant gift packaging",
         "home-decor", True, ["Shape"], ["Square", "Round"]),
        ("Creative Washi Tape Collection", "washi-tape-collection", 12.99, 22.99,
         "Set of 12 decorative washi tapes. Unique patterns designed by independent artists.\n- 12 rolls, 10mm wide\n- 5 meters per roll\n- Washi paper, repositionable\n- Patterns: geometric, floral, abstract",
         "stationery", True, [], []),
        ("Brass Wire Sculpture", "brass-wire-sculpture", 44.99, 79.99,
         "Hand-bent brass wire sculpture. Abstract organic form adds artistic flair to any shelf.\n- Height: 12 inches\n- Material: Solid brass, lacquered finish\n- Base: Black marble\n- No two exactly alike",
         "home-decor", True, ["Form"], ["Tree", "Figure", "Abstract"]),
        ("Creative Pendant Light", "creative-pendant-light", 54.99, 89.99,
         "Designer pendant light with woven rattan shade. Warm ambient lighting.\n- Shade diameter: 14 inches\n- Cable length: adjustable up to 59 inches\n- Bulb: E26, max 60W (not included)\n- UL listed",
         "home-decor", True, ["Color"], ["Natural Rattan", "Black Rattan", "White Rattan"]),
        ("Hand-lettered Quote Print", "hand-lettered-quote-print", 16.99, 29.99,
         "Inspirational hand-lettered quote print. Motivational wall art for home or office.\n- Size: 11x14 inches\n- Printed on premium matte paper\n- Frame not included\n- Multiple quotes available",
         "art-prints", True, ["Quote"], ["Dream Big", "Stay Curious", "Be Bold"]),
        ("Leather Bookmark Set", "leather-bookmark-set", 14.99, 24.99,
         "Set of 3 genuine leather bookmarks with embossed designs. Perfect for book lovers.\n- 3 bookmarks with different patterns\n- Genuine top-grain leather\n- Gift box included\n- Tassel detail",
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
