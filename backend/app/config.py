import os

class Config:
    # Use DATABASE_URL if provided, else fallback to a local SQLite file
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secrets
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
