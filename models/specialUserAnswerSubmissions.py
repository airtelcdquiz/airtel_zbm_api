from models.user import db
from datetime import datetime

class SpecialUserAnswerSubmissions(db.Model):
    __tablename__ = 'specialUserAnswerSubmissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    special_tracker_id = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer)
    question_type = db.Column(db.String(255))
    campaign_id = db.Column(db.String(255))
    school_id = db.Column(db.String(255))
    user_id = db.Column(db.String(255))
    response_code = db.Column(db.Integer)
    participant_phone = db.Column(db.String(255))
    question_ans = db.Column(db.String(255))
    is_ans_correct = db.Column(db.Enum('0', '1'))
    points = db.Column(db.Integer)
    date = db.Column(db.Date)
    channel = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'special_tracker_id': self.special_tracker_id,
            'question_id': self.question_id,
            'question_type': self.question_type,
            'campaign_id': self.campaign_id,
            'school_id': self.school_id,
            'user_id': self.user_id,
            'response_code': self.response_code,
            'participant_phone': self.participant_phone,
            'question_ans': self.question_ans,
            'is_ans_correct': self.is_ans_correct,
            'points': self.points,
            'date': self.date.isoformat() if self.date else None,
            'channel': self.channel,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 