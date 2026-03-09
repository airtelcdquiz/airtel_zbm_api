from datetime import datetime
from .database import db
# from .user import User
class School(db.Model):
    __tablename__ = 'schools'  # Utilise la table existante 'schools'
    
    code = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 

    def to_dict(self):
        return {
            'id': self.id,
            'idcode': self.code,
            'name': self.name,
            # 'created_at': self.created_at.isoformat(),
            # 'updated_at': self.updated_at.isoformat(),
            # 'users_with_school': [user.to_dict() for user in self.users_with_school]
        } 