from app.extensions import db
from datetime import datetime

class WorkerApplication(db.Model):
    __tablename__ = "worker_applications"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)  # optional AI-enhanced description
    status = db.Column(db.String(50), default="pending")  # pending, accepted, rejected
    ai_score = db.Column(db.Float, nullable=True)  # optional AI ranking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    job = db.relationship("Job", backref="applications")
    worker = db.relationship("User", backref="applications")

    def __repr__(self):
        return f"<Application {self.id} for Job {self.job_id}>"
