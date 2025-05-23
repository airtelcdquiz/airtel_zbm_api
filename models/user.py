from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from .database import db
from .role import Role
from .permission import Permission
# from .school import School
from .user_role import user_roles
from .user_permission import user_permissions
from .attached_school import AttachedSchool

class User(db.Model):
    __tablename__ = 'users'  # Utilise la table existante 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(100), unique=True, nullable=False)
    # password = db.Column(db.String(100), nullable=False)
    # is_active = db.Column(db.Boolean, default=True)
    participant_phone = db.Column(db.String(255), unique=True, nullable=False)
    participant_full_name = db.Column(db.String(255), unique=True, nullable=False)
    participant_category = db.Column(db.String(255), unique=True, nullable=False)
    participant_class = db.Column(db.String(255), unique=True, nullable=False)
    # participant_school = db.Column(db.String(255), unique=True, nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_superuser = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)

    # Relations many-to-many avec les rôles et permissions
    roles = db.relationship(Role, secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    direct_permissions = db.relationship(Permission, secondary=user_permissions, backref=db.backref('users', lazy='dynamic'))
    
    # Relation avec les écoles attachées
    # attached_schools = db.relationship('School', 
    #                                 secondary='attached_schools',
    #                                 backref=db.backref('users_with_school', lazy='dynamic'))

    def get_all_permissions(self):
        """Récupère toutes les permissions de l'utilisateur (via les rôles et directement)"""
        permissions = set()
        
        # Permissions des rôles
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        
        # Permissions directes
        for permission in self.direct_permissions:
            permissions.add(permission.name)
            
        return list(permissions)

    def to_dict(self):
        return {
            'id': self.id,
            # 'email': self.email,
            # 'password': self.password,
            # 'is_active': self.is_active,
            'participant_phone': self.participant_phone,
            'participant_full_name': self.participant_full_name,
            'participant_category': self.participant_category,
            'participant_class': self.participant_class,
            # 'participant_school': self.participant_school,
            'created_at': self.created_at.isoformat(),
            'is_superuser': self.is_superuser,
            'is_active': self.is_active,
            'school_id': self.school_id,
            # 'attached_schools': [school.to_dict() for school in self.attached_schools]
        }
    
    def get_all_roles(self):
        return [role.name for role in self.roles]