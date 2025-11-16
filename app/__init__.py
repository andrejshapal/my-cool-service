from flask import Flask

from app.api import api_bp
from app.extensions import db, bcrypt, ma, migrate
from config import config_by_name
from flask_migrate import Migrate

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    with app.app_context():
        register_extensions(app)
        app.register_blueprint(api_bp, url_prefix="/api")
    return app

def register_extensions(app):
    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)