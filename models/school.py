from datetime import datetime
from .database import db

class School(db.Model):
    __tablename__ = 'schools'  # Utilise la table existante 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    idcode = db.Column(db.String(255), unique=True, nullable=False)
    schoolname = db.Column(db.String(255), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'idcode': self.idcode,
            'schoolname': self.schoolname,
            # 'created_at': self.created_at.isoformat(),
            # 'updated_at': self.updated_at.isoformat()
        } 