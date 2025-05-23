from datetime import datetime
from .database import db

class AttachedSchool(db.Model):
    __tablename__ = 'attached_schools'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec des références de chaîne pour éviter les imports circulaires
    user = db.relationship('User', backref=db.backref('attached_schools_association', lazy='dynamic'))
    school = db.relationship('School', backref=db.backref('attached_schools_association', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'school_id': self.school_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 