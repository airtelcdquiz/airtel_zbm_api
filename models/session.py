from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    expire_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.expire_at = datetime.utcnow() + timedelta(days=1)  # Session valide pendant 1 jour

    def is_valid(self):
        return datetime.utcnow() < self.expire_at

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'user_id': self.user_id,
            'create_at': self.create_at.isoformat(),
            'expire_at': self.expire_at.isoformat()
        } 