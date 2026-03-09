from .database import db

# Table d'association pour la relation many-to-many entre User et Permission
user_permissions = db.Table('user_permissions',
    db.Column('phone_number', db.String(255), db.ForeignKey('users.phone_number'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
) 