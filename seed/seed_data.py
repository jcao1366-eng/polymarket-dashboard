"""Seed the database with sample products."""
from app import create_app
from models import db, Product, Category, ProductVariant
import random

def seed():
    app = create_app()
    with app.app_context():
        # Categories
        cats = [
            Category(name="Home & Living", slug="home-living", description="Beautiful home decor and essentials", sort_order=1),
            Category(name="Tech Gadgets", slug="tech-gadgets", description="Cool tech accessories and gadgets", sort_order=2),
            Category(name="Fashion", slug="fashion", description="Trendy fashion accessories", sort_order=3),
            Category(name="Health & Beauty", slug="health-beauty", description="Personal care and wellness", sort_order=4),
        ]
        for c in cats:
            if not Category.query.filter_by(slug=c.slug).first():
                db.session.add(c)
        db.session.commit()

        all_cats = Category.query.all()

        # Products
        products_data = [
            ("Minimalist Desk Lamp", "minimalist-desk-lamp", 29.99, 49.99, "Elegant LED desk lamp with touch dimmer. 3 color temperatures. USB charging port.", "home-living", True),
            ("Wireless Charging Pad", "wireless-charging-pad", 19.99, 34.99, "Slim 15W wireless charger compatible with all Qi devices. LED indicator.", "tech-gadgets", True),
            ("Canvas Tote Bag", "canvas-tote-bag", 24.99, 39.99, "Organic cotton tote bag. Reinforced handles. Interior pocket. Machine washable.", "fashion", True),
            ("Aromatherapy Diffuser", "aromatherapy-diffuser", 34.99, 59.99, "Ultrasonic essential oil diffuser. 7 LED colors. Auto shut-off. 300ml capacity.", "home-living", True),
            ("Bluetooth Earbuds", "bluetooth-earbuds", 39.99, 69.99, "True wireless earbuds with ANC. 30hr battery. IPX5 waterproof. Touch controls.", "tech-gadgets", True),
            ("Silk Sleep Mask", "silk-sleep-mask", 14.99, 24.99, "100% mulberry silk sleep mask. Adjustable strap. Zero pressure on eyes.", "health-beauty", True),
            ("Bamboo Cutting Board", "bamboo-cutting-board", 22.99, 36.99, "Organic bamboo cutting board. Juice groove. Easy-grip handles. Eco-friendly.", "home-living", True),
            ("Phone Tripod Stand", "phone-tripod-stand", 16.99, 29.99, "Adjustable phone tripod. 360 degree rotation. Bluetooth remote included.", "tech-gadgets", True),
            ("Crystal Water Bottle", "crystal-water-bottle", 28.99, 44.99, "Glass water bottle with real crystal wand. BPA free. 500ml. Protective sleeve.", "health-beauty", True),
            ("Leather Card Holder", "leather-card-holder", 18.99, 32.99, "Genuine leather card holder. 6 card slots. RFID blocking. Slim profile.", "fashion", True),
            ("Smart LED Strip Lights", "smart-led-strip-lights", 21.99, 39.99, "16.4ft RGB LED strip. App control. Music sync. Multiple modes.", "tech-gadgets", True),
            ("Yoga Mat Premium", "yoga-mat-premium", 32.99, 54.99, "6mm premium yoga mat. Non-slip surface. Eco-friendly TPE material. Carry strap included.", "health-beauty", True),
        ]

        for name, slug, price, compare, desc, cat_slug, featured in products_data:
            if Product.query.filter_by(slug=slug).first():
                continue
            p = Product(
                name=name, slug=slug, base_price=price, compare_price=compare,
                description=desc, is_featured=featured,
                image_url=f"https://placehold.co/600x600/e9d5ff/7C3AED?text={name[:10]}",
                images=[f"https://placehold.co/600x600/f5f3ff/7C3AED?text={name[:8]}+2"],
            )
            cat = next((c for c in all_cats if c.slug == cat_slug), None)
            if cat:
                p.categories.append(cat)
            # Add default variant
            p.variants.append(ProductVariant(sku=f"SKU-{slug[:8].upper()}", options={"Color": "Default"}, stock=999))
            db.session.add(p)

        db.session.commit()
        print(f"Seeded {len(products_data)} products across {len(all_cats)} categories.")

if __name__ == "__main__":
    seed()
