from .database import db

# Table d'association pour la relation many-to-many entre User et Role
user_roles = db.Table('user_roles',
    db.Column('phone_number', db.String(255), db.ForeignKey('users.phone_number'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
) 