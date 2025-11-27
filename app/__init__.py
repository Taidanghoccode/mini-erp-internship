from flask import Flask
from app.db.db import db
from app.db.config import Config
from app.db.init_models import load_models  


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        load_models()
        db.create_all()
        print("Database tables created successfully.")

    from app.api.health_controller import bp as health_bp
    app.register_blueprint(health_bp, url_prefix="/api")

    return app
