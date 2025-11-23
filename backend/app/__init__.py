from app.models import application
from flask import Flask
from app.extensions import db, migrate, jwt
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import blueprints inside factory to avoid import-time side effects
    from routes.auth import auth_bp
    from routes.workers import worker_bp
    from routes.jobs import jobs_bp
    from routes.applications import application_bp

    # Register blueprints with a single API prefix
    # auth_bp already uses the internal prefix '/auth', so register it under '/api'
    # to yield endpoints like '/api/auth/register'
    app.register_blueprint(auth_bp, url_prefix='/api')
    # yields /api/workers/... endpoint
    app.register_blueprint(worker_bp, url_prefix='/api')
    # yields /api/jobs/... endpoint
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    # yields /api/applications/... endpoint
    app.register_blueprint(application_bp, url_prefix='/api/applications')
    return app
