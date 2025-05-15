from datetime import datetime
from .database import db

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Permission {self.name}>'

# Table d'association pour la relation many-to-many entre Role et Permission
# role_permissions = db.Table('role_permissions',
#     db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
#     db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
# ) 