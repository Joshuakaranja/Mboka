from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.job import Job
from app.utils.security import login_required

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


# ---------------- CREATE JOB ---------------- #
@jobs_bp.post("/")
@login_required
def create_job(current_user):
    data = request.json or {}

    required_fields = ["title", "description", "location"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Accept either explicit lat/lng or a location string. For testing, if lat/lng
    # are not provided, store 0.0 and keep the original location in metadata.
    location_lat = data.get("location_lat")
    location_lng = data.get("location_lng")
    location_str = data.get("location")
    if location_lat is None or location_lng is None:
        location_lat = 0.0
        location_lng = 0.0

    job = Job(
        title=data["title"],
        description=data["description"],
        price=data.get("price"),
        location_lat=location_lat,
        location_lng=location_lng,
        client_id=current_user.id,
        job_metadata={"location": location_str} if location_str else None,
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created", "job": job.serialize()}), 201


# ---------------- GET ALL JOBS ---------------- #
@jobs_bp.get("/")
def get_all_jobs():
    # Pagination support
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    if per_page > 100:
        per_page = 100

    pagination = Job.query.paginate(
        page=page, per_page=per_page, error_out=False)
    jobs = pagination.items
    result = {
        "items": [job.serialize() for job in jobs],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
    return jsonify(result), 200


# ---------------- GET SINGLE JOB ---------------- #
@jobs_bp.get("/<int:job_id>")
def get_single_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job.serialize()), 200


# ---------------- UPDATE JOB ---------------- #
@jobs_bp.put("/<int:job_id>")
@login_required
def update_job(current_user, job_id):
    data = request.json or {}
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Only owner can edit
    if job.client_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    job.title = data.get("title", job.title)
    job.description = data.get("description", job.description)
    job.price = data.get("price", job.price)
    job.location_lat = data.get("location_lat", job.location_lat)
    job.location_lng = data.get("location_lng", job.location_lng)
    if data.get("location"):
        job.job_metadata = job.job_metadata or {}
        job.job_metadata["location"] = data.get("location")

    db.session.commit()
    return jsonify({"message": "Job updated", "job": job.serialize()}), 200


# ---------------- DELETE JOB ---------------- #
@jobs_bp.delete("/<int:job_id>")
@login_required
def delete_job(current_user, job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.client_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"}), 200
