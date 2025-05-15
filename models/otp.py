from datetime import datetime, timedelta
from .database import db

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_phone = db.Column(db.String(255), nullable=False)
    Otp = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    def __init__(self, participant_phone, Otp):
        self.participant_phone = participant_phone
        self.Otp = Otp
        self.expires_at = datetime.utcnow() + timedelta(minutes=5)  # OTP valide pendant 5 minutes

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'participant_phone': self.participant_phone,
            'Otp': self.Otp,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_used': self.is_used
        } 