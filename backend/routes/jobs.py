from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.user import User
from config import engine
from app.utils.auth_decorators import login_required

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")

# ---------------- CREATE JOB ---------------- #
@jobs_bp.post("/")
@login_required
def create_job(user_id):
    data = request.json

    required_fields = ["title", "description", "location"]

    # Validate
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    with Session(engine) as session:
        job = Job(
            title=data["title"],
            description=data["description"],
            location=data["location"],
            user_id=user_id,
        )
        session.add(job)
        session.commit()

        return jsonify({"message": "Job created", "job": job.serialize()}), 201


# ---------------- GET ALL JOBS ---------------- #
@jobs_bp.get("/")
def get_all_jobs():
    with Session(engine) as session:
        jobs = session.query(Job).all()
        return jsonify([job.serialize() for job in jobs]), 200


# ---------------- GET SINGLE JOB ---------------- #
@jobs_bp.get("/<int:job_id>")
def get_single_job(job_id):
    with Session(engine) as session:
        job = session.get(Job, job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        return jsonify(job.serialize()), 200


# ---------------- UPDATE JOB ---------------- #
@jobs_bp.put("/<int:job_id>")
@login_required
def update_job(user_id, job_id):
    data = request.json

    with Session(engine) as session:
        job = session.get(Job, job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Only owner can edit
        if job.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        job.title = data.get("title", job.title)
        job.description = data.get("description", job.description)
        job.location = data.get("location", job.location)

        session.commit()

        return jsonify({"message": "Job updated", "job": job.serialize()}), 200


# ---------------- DELETE JOB ---------------- #
@jobs_bp.delete("/<int:job_id>")
@login_required
def delete_job(user_id, job_id):
    with Session(engine) as session:
        job = session.get(Job, job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        if job.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        session.delete(job)
        session.commit()

        return jsonify({"message": "Job deleted"}), 200
