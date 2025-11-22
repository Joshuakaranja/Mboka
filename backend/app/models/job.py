from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)  # optional, AI may set
    location_lat = db.Column(db.Float, nullable=False)
    location_lng = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # assigned worker
    status = db.Column(db.String(50), default="open")  # open, assigned, completed, cancelled

    job_metadata = db.Column(JSON, nullable=True)  # optional AI data: price reason, flags

    # Relationships
    client = db.relationship("User", foreign_keys=[client_id], backref="posted_jobs")
    worker = db.relationship("User", foreign_keys=[worker_id], backref="assigned_jobs")

    def __repr__(self):
        return f"<Job {self.title} ({self.status})>"
