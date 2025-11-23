import datetime
import jwt
from flask import current_app, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app.models.user import User

# -------- PASSWORD SECURITY -------- #


def hash_password(password: str) -> str:
    """Hash plain password using Werkzeug."""
    return generate_password_hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Compare stored hash with user input."""
    return check_password_hash(hashed_password, plain_password)


# -------- JWT GENERATION -------- #

def create_access_token(user_id: int) -> str:
    """Create a short-lived JWT (access token)."""
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "type": "access"
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    """Create a long-lived JWT (refresh token)."""
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str):
    """Decode JWT and return payload, raises error if invalid."""
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])


# -------- LOGIN REQUIRED DECORATOR -------- #

def login_required(f):
    """
    Protect routes requiring authentication.
    Passes current_user to the route if token is valid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Accept token either from Authorization header (Bearer) or from cookies
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        else:
            token = request.cookies.get("access_token")

        if not token:
            return jsonify({"error": "Authentication required. Provide 'Authorization: Bearer <token>' header or 'access_token' cookie."}), 401
        try:
            payload = decode_token(token)
            user = User.query.get(payload["sub"])
            if not user:
                return jsonify({"error": "User not found"}), 404
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(user, *args, **kwargs)
    return decorated
