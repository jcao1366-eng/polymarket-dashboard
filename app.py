from flask import Flask
from config import Config
from models import db
from routes.main import main_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.checkout_routes import checkout_bp
from routes.api_routes import api_bp
from routes.admin_routes import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        from models import Product, Category, ProductVariant, ProductReview, Order, OrderItem, Customer, CartItem
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
