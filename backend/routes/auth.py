from flask import Blueprint, request, jsonify, current_app, make_response
from app.models.user import User
from app.extensions import db
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from functools import wraps
import datetime

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

# -------------------------
# AUTH DECORATOR
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        try:
            payload = decode_token(token)
            user = User.query.get(payload["sub"])
            if not user:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(user, *args, **kwargs)
    return decorated

# -------------------------
# REGISTER
# -------------------------
@auth_bp.post("/register")
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "worker")  # default worker

    if User.query.filter((User.username==username)|(User.email==email)).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# -------------------------
# LOGIN
# -------------------------
@auth_bp.post("/login")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response = make_response(jsonify({"message": "Login successful"}))
    # Set HTTP-only cookies
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite="Strict",
        secure=current_app.config.get("ENV") == "production",
        max_age=30*60  # 30 min
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite="Strict",
        secure=current_app.config.get("ENV") == "production",
        max_age=7*24*3600  # 7 days
    )
    return response

# -------------------------
# REFRESH ACCESS TOKEN
# -------------------------
@auth_bp.post("/refresh")
def refresh():
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token missing"}), 401
    try:
        payload = decode_token(refresh_token)
        user = User.query.get(payload["sub"])
        if not user:
            return jsonify({"error": "User not found"}), 404
        new_access = create_access_token(user.id)
    except Exception as e:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    response = make_response(jsonify({"message": "Token refreshed"}))
    response.set_cookie(
        "access_token",
        new_access,
        httponly=True,
        samesite="Strict",
        secure=current_app.config.get("ENV") == "production",
        max_age=30*60
    )
    return response

# -------------------------
# LOGOUT
# -------------------------
@auth_bp.post("/logout")
def logout():
    response = make_response(jsonify({"message": "Logged out"}))
    response.set_cookie("access_token", "", expires=0)
    response.set_cookie("refresh_token", "", expires=0)
    return response

# -------------------------
# GET CURRENT USER
# -------------------------
@auth_bp.get("/me")
@login_required
def me(user):
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })
