from ..extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'worker' or 'client'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    worker_profile = db.relationship('WorkerProfile', backref='user', uselist=False)

    #one to many relationships defined in Job and WorkerApplication models

    jobs = db.relationship('Job', backref='client', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
