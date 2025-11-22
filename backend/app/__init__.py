from flask import Flask
from app.extensions import db, migrate, jwt
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # <-- important
    jwt.init_app(app)

    # Import blueprints inside factory to avoid import-time side effects
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app
