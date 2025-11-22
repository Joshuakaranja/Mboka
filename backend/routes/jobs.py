from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.job import Job
from app.models.user import User
from app.utils.security import login_required

jobs_bp = Blueprint("jobs_bp", __name__, url_prefix="/jobs")

# ------------------------
# Create Job
# ------------------------
@jobs_bp.post("/")
@login_required
def create_job(current_user):
    data = request.json
    title = data.get("title")
    description = data.get("description")
    price = data.get("price")  # optional, AI may fill
    location_lat = data.get("location_lat")
    location_lng = data.get("location_lng")

    if not all([title, description, location_lat, location_lng]):
        return jsonify({"error": "Missing required fields"}), 400

    job = Job(
        title=title,
        description=description,
        price=price,
        location_lat=location_lat,
        location_lng=location_lng,
        client_id=current_user.id
    )

    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Job created", "job_id": job.id}), 201

# ------------------------
# List Jobs (with optional nearby filter)
# ------------------------
@jobs_bp.get("/")
def list_jobs():
    # For now, simple: list all jobs
    jobs = Job.query.filter(Job.status=="open").all()
    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "price": job.price,
            "location_lat": job.location_lat,
            "location_lng": job.location_lng,
            "status": job.status
        })
    return jsonify(result)

# ------------------------
# Job Details
# ------------------------
@jobs_bp.get("/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify({
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "price": job.price,
        "location_lat": job.location_lat,
        "location_lng": job.location_lng,
        "status": job.status,
        "client_id": job.client_id,
        "worker_id": job.worker_id
    })
