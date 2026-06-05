from models import Product, Category, db

def get_featured_products(limit=8):
    return Product.query.filter_by(is_active=True, is_featured=True).order_by(Product.created_at.desc()).limit(limit).all()

def get_products(page=1, per_page=12, category_slug=None, sort="newest", search=None):
    q = Product.query.filter_by(is_active=True)
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            q = q.filter(Product.categories.contains(cat))
    if search:
        q = q.filter(db.or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%")))
    if sort == "price_asc":
        q = q.order_by(Product.base_price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.base_price.desc())
    elif sort == "popular":
        q = q.order_by(Product.created_at.desc())
    else:
        q = q.order_by(Product.created_at.desc())
    return q.paginate(page=page, per_page=per_page, error_out=False)

def get_product_by_slug(slug):
    return Product.query.filter_by(slug=slug, is_active=True).first_or_404()

def get_categories():
    return Category.query.order_by(Category.sort_order).all()
