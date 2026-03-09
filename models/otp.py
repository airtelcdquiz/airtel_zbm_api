from datetime import datetime, timedelta
from .database import db

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(255), nullable=False)
    otp = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    def __init__(self, phone_number, otp):
        self.phone_number = phone_number
        self.otp = otp
        self.expires_at = datetime.utcnow() + timedelta(minutes=5)  # OTP valide pendant 5 minutes

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'otp': self.otp,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_used': self.is_used
        } 