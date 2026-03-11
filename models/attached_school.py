from datetime import datetime
from .database import db

from models.school import School
from models.attached_school import AttachedSchool
from models.user import User

class AttachedSchool(db.Model):
    __tablename__ = 'attached_schools'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(255), db.ForeignKey('users.phone_number', ondelete='CASCADE'), nullable=False)
    code = db.Column(db.String(255), db.ForeignKey('schools.code', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec des références de chaîne pour éviter les imports circulaires
    user = db.relationship('User', backref=db.backref('attached_schools_association', lazy='dynamic'))
    school = db.relationship('School', backref=db.backref('attached_schools_association', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'code': self.code,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 