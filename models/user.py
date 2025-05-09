from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # Utilise la table existante 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # email = db.Column(db.String(100), unique=True, nullable=False)
    # password = db.Column(db.String(100), nullable=False)
    # is_active = db.Column(db.Boolean, default=True)
    # is_superuser = db.Column(db.Boolean, default=False)
    participant_phone = db.Column(db.String(255), unique=True, nullable=False)
    participant_full_name = db.Column(db.String(255), unique=True, nullable=False)
    participant_category = db.Column(db.String(255), unique=True, nullable=False)
    participant_class = db.Column(db.String(255), unique=True, nullable=False)
    # participant_school = db.Column(db.String(255), unique=True, nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            # 'email': self.email,
            # 'password': self.password,
            # 'is_active': self.is_active,
            # 'is_superuser': self.is_superuser,
            'participant_phone': self.participant_phone,
            'participant_full_name': self.participant_full_name,
            'participant_category': self.participant_category,
            'participant_class': self.participant_class,
            # 'participant_school': self.participant_school,
            'created_at': self.created_at.isoformat()
        }