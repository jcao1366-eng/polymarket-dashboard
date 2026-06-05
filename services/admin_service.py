from models import Product, ProductVariant, Category, Order, OrderItem, db
from flask import current_app

def verify_admin(username, password):
    return (username == current_app.config["ADMIN_USERNAME"]
            and password == current_app.config["ADMIN_PASSWORD"])

def get_orders(page=1, per_page=20):
    return Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

def search_orders(q="", status="", page=1, per_page=20):
    query = Order.query
    if status:
        query = query.filter(Order.status == status)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            db.or_(
                Order.order_number.ilike(pattern),
                Order.email.ilike(pattern),
                Order.first_name.ilike(pattern),
                Order.last_name.ilike(pattern),
            )
        )
    return query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

def update_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    return order

def update_order_tracking(order_id, tracking_number):
    order = Order.query.get_or_404(order_id)
    order.tracking_number = tracking_number
    if tracking_number and order.status == "paid":
        order.status = "shipped"
    db.session.commit()
    return order

def get_all_products():
    return Product.query.order_by(Product.created_at.desc()).all()

def search_products(q="", status=""):
    query = Product.query
    if status == "active":
        query = query.filter(Product.is_active == True)
    elif status == "draft":
        query = query.filter(Product.is_active == False)
    elif status == "featured":
        query = query.filter(Product.is_featured == True)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(pattern),
                Product.slug.ilike(pattern),
            )
        )
    return query.order_by(Product.created_at.desc()).all()

def get_product(product_id):
    return Product.query.get_or_404(product_id)

def create_product(data):
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', data.get("slug") or data.get("name", "").lower()).strip("-")
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
    if data.get("categories"):
        for cid in data["categories"]:
            cat = Category.query.get(int(cid))
            if cat:
                p.categories.append(cat)
    db.session.add(p)
    db.session.flush()
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
    return [url.strip() for url in images_str.strip().split("\n") if url.strip()]

def _save_variants(product, data):
    if "variant_options" in data:
        ProductVariant.query.filter_by(product_id=product.id).delete()
        options = data["variant_options"]
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
