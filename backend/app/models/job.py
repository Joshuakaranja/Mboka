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

    client_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), nullable=True)  # assigned worker
    # open, assigned, completed, cancelled
    status = db.Column(db.String(50), default="open")

    # optional AI data: price reason, flags
    job_metadata = db.Column(JSON, nullable=True)

    # Relationships
    client = db.relationship("User", foreign_keys=[
                             client_id], backref="posted_jobs")
    worker = db.relationship("User", foreign_keys=[
                             worker_id], backref="assigned_jobs")

    def __repr__(self):
        return f"<Job {self.title} ({self.status})>"

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "location_lat": self.location_lat,
            "location_lng": self.location_lng,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "client_id": self.client_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "job_metadata": self.job_metadata,
        }
