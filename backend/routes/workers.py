from flask import Blueprint, request, jsonify
from app.models import WorkerProfile
from app.extensions import db

worker_bp = Blueprint('worker_bp', __name__, url_prefix="/workers")

# -------------------------------
# Fetch worker profile
# -------------------------------
@worker_bp.get("/<int:worker_id>")
def get_worker(worker_id):
    worker = WorkerProfile.query.get(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404

    return jsonify({
        "id": worker.id,
        "skills": worker.skills,
        "bio": worker.bio,
        "rating": worker.rating,
        "is_available": worker.is_available,
        "available_hours": worker.available_hours,
        "location": {
            "lat": worker.latitude,
            "lng": worker.longitude
        }
    })

# -------------------------------
# Update skills
# -------------------------------
@worker_bp.patch("/<int:worker_id>/skills")
def update_skills(worker_id):
    data = request.json
    new_skills = data.get("skills")

    if not isinstance(new_skills, list):
        return jsonify({"error": "Skills must be a list"}), 400

    worker = WorkerProfile.query.get(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404

    worker.skills = new_skills
    db.session.commit()

    return jsonify({"message": "Skills updated", "skills": worker.skills})

# -------------------------------
# Toggle availability
# -------------------------------
@worker_bp.patch("/<int:worker_id>/availability")
def update_availability(worker_id):
    data = request.json
    hours = data.get("hours", 0)

    worker = WorkerProfile.query.get(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404

    worker.is_available = hours > 0
    worker.available_hours = hours

    db.session.commit()

    return jsonify({
        "message": "Availability updated",
        "is_available": worker.is_available,
        "hours": worker.available_hours
    })

# -------------------------------
# Update location
# -------------------------------
@worker_bp.patch("/<int:worker_id>/location")
def update_location(worker_id):
    data = request.json
    lat = data.get("lat")
    lng = data.get("lng")

    if lat is None or lng is None:
        return jsonify({"error": "lat & lng required"}), 400

    worker = WorkerProfile.query.get(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404

    worker.latitude = lat
    worker.longitude = lng
    db.session.commit()

    return jsonify({"message": "Location updated"})

# -------------------------------
# Nearby workers (simple radius)
# -------------------------------
@worker_bp.get("/")
def workers_nearby():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)

    if lat is None or lng is None:
        return jsonify({"error": "lat & lng query params required"}), 400

    workers = WorkerProfile.query.all()

    results = []
    for w in workers:
        if w.latitude is None or w.longitude is None:
            continue

        dist = ((w.latitude - lat)**2 + (w.longitude - lng)**2) ** 0.5
        if dist <= 0.05:  # approx 3km (placeholder)
            results.append({
                "id": w.id,
                "skills": w.skills,
                "lat": w.latitude,
                "lng": w.longitude,
                "distance": round(dist, 4)
            })

    return jsonify(results)
