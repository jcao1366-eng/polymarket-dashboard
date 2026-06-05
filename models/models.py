from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

product_category = db.Table(
    "product_category",
    db.Column("product_id", db.Integer, db.ForeignKey("products.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True),
)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    image_url = db.Column(db.String(500), default="")
    sort_order = db.Column(db.Integer, default=0)
    products = db.relationship("Product", secondary=product_category, back_populates="categories")

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    description_en = db.Column(db.Text, default="")
    base_price = db.Column(db.Float, nullable=False)
    compare_price = db.Column(db.Float, default=0)
    cost_price = db.Column(db.Float, default=0)
    supplier_url = db.Column(db.String(500), default="")
    image_url = db.Column(db.String(500), default="")
    images = db.Column(db.JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    seo_title = db.Column(db.String(200), default="")
    seo_description = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    categories = db.relationship("Category", secondary=product_category, back_populates="products")
    variants = db.relationship("ProductVariant", backref="product", lazy="dynamic")
    reviews = db.relationship("ProductReview", backref="product", lazy="dynamic")

    @property
    def display_price(self):
        return self.base_price

    @property
    def discount_pct(self):
        if self.compare_price and self.compare_price > self.base_price:
            return round((1 - self.base_price / self.compare_price) * 100)
        return 0

class ProductVariant(db.Model):
    __tablename__ = "product_variants"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    sku = db.Column(db.String(100), default="")
    options = db.Column(db.JSON, default=dict)
    price_modifier = db.Column(db.Float, default=0)
    stock = db.Column(db.Integer, default=999)
    is_active = db.Column(db.Boolean, default=True)

class ProductReview(db.Model):
    __tablename__ = "product_reviews"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    author = db.Column(db.String(100), default="Anonymous")
    rating = db.Column(db.Integer, default=5)
    content = db.Column(db.Text, default="")
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default="pending")
    email = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100), default="")
    last_name = db.Column(db.String(100), default="")
    address_line1 = db.Column(db.String(200), default="")
    address_line2 = db.Column(db.String(200), default="")
    city = db.Column(db.String(100), default="")
    state = db.Column(db.String(100), default="")
    zip_code = db.Column(db.String(20), default="")
    country = db.Column(db.String(3), default="US")
    phone = db.Column(db.String(30), default="")
    subtotal = db.Column(db.Float, default=0)
    shipping = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default="USD")
    stripe_session_id = db.Column(db.String(200), default="")
    tracking_number = db.Column(db.String(100), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy="dynamic")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(200), default="")
    product_slug = db.Column(db.String(220), default="")
    variant_info = db.Column(db.String(200), default="")
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(500), default="")

class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), default="")
    last_name = db.Column(db.String(100), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(200), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship("Product")
    variant = db.relationship("ProductVariant")

class PageView(db.Model):
    __tablename__ = "page_views"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), nullable=False, index=True)
    ip = db.Column(db.String(45), default="")
    user_agent = db.Column(db.String(500), default="")
    referrer = db.Column(db.String(500), default="")
    country = db.Column(db.String(3), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
