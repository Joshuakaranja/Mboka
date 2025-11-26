from app.models import application
from flask import Flask
from app.extensions import db, migrate, jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Basic logging configuration
    if not app.debug:
        handler = RotatingFileHandler(
            'logs/kazilink.log', maxBytes=1000000, backupCount=3)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

    # Rate limiter (uses remote address by default)
    limiter = Limiter(key_func=get_remote_address)
    limiter.init_app(app)

    # Import blueprints inside factory to avoid import-time side effects
    from routes.auth import auth_bp
    from routes.workers import worker_bp
    from routes.jobs import jobs_bp
    from routes.applications import application_bp

    # Register blueprints with a single API prefix
    # auth_bp already uses the internal prefix '/auth', so register it under '/api'
    # to yield endpoints like '/api/auth/register'
    # Register all blueprints under the common '/api' prefix so final
    # endpoints are '/api/auth', '/api/workers', '/api/jobs', '/api/applications'
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(worker_bp, url_prefix='/api')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    app.register_blueprint(application_bp, url_prefix='/api')
    return app
