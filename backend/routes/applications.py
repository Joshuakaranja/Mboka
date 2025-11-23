from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.application import WorkerApplication
from app.models.job import Job
from app.utils.security import login_required

application_bp = Blueprint("application_bp", __name__, url_prefix="/applications")

# ------------------------
# Worker applies to job
# ------------------------
@application_bp.post("/")
@login_required
def apply_to_job(current_user):
    data = request.json
    job_id = data.get("job_id")
    cover_letter = data.get("cover_letter", "")

    # Check if job exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Prevent duplicate application
    existing = WorkerApplication.query.filter_by(job_id=job_id, worker_id=current_user.id).first()
    if existing:
        return jsonify({"error": "You have already applied to this job"}), 400

    app = WorkerApplication(
        job_id=job_id,
        worker_id=current_user.id,
        cover_letter=cover_letter
    )

    db.session.add(app)
    db.session.commit()
    return jsonify({"message": "Application submitted", "application_id": app.id}), 201

# ------------------------
# List applications for a job (client view)
# ------------------------
@application_bp.get("/job/<int:job_id>")
@login_required
def list_applications(current_user, job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Only job owner can view
    if job.client_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    result = []
    for app in job.applications:
        result.append({
            "id": app.id,
            "worker_id": app.worker_id,
            "cover_letter": app.cover_letter,
            "status": app.status,
            "ai_score": app.ai_score
        })
    return jsonify(result)
