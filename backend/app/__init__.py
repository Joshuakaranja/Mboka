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

    # Register blueprints with a single API prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(worker_bp, url_prefix='/api')  # yields /api/workers/... endpoint
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')  # yields /api/jobs/... endpoint
    return app
