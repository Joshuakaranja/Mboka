from ..extensions import db

class WorkerProfile(db.Model):
    __tablename__ = "worker_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Example profile fields
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)  # could be JSON in a more advanced schema
    location = db.Column(db.String(255))
