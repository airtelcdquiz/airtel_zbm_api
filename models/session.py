from datetime import datetime, timedelta, timezone
from .database import db

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(255), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    expire_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, phone_number):
        self.token = token
        self.phone_number = phone_number
        self.expire_at = datetime.utcnow() + timedelta(days=1)  # Session valide pendant 1 jour

    def is_valid(self):
        # expire_at peut etre naif (colonne TIMESTAMP) ou aware (TIMESTAMPTZ,
        # cas de la base de prod) selon le type de colonne. On compare dans le
        # meme referentiel pour eviter "can't compare offset-naive and
        # offset-aware datetimes".
        expire_at = self.expire_at
        if expire_at is None:
            return False
        if expire_at.tzinfo is not None:
            return datetime.now(timezone.utc) < expire_at
        return datetime.utcnow() < expire_at

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'phone_number': self.phone_number,
            'create_at': self.create_at.isoformat(),
            'expire_at': self.expire_at.isoformat()
        } 