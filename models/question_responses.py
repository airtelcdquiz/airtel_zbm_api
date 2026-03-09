from models.user import db
from datetime import datetime

class QuestionResponse(db.Model):
    __tablename__ = 'question_responses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #special_tracker_id = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer)
    #question_type = db.Column(db.String(255))
    #campaign_id = db.Column(db.String(255))
    #code = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    choice = db.Column(db.Integer)
    #participant_phone = db.Column(db.String(255))
    #question_ans = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean())
    #points = db.Column(db.Integer)
    created_date = db.Column(db.Date)
    #channel = db.Column(db.String(255))
    #created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            #'special_tracker_id': self.special_tracker_id,
            'question_id': self.question_id,
            #'question_type': self.question_type,
            #'campaign_id': self.campaign_id,
            #'code': self.code,
            'phone_number': self.phone_number,
            'choice': self.choice,
            #'participant_phone': self.participant_phone,
            #'question_ans': self.question_ans,
            'is_correct': self.is_correct,
            #'points': self.points,
            'created_date': self.date.isoformat() if self.date else None,
            #'channel': self.channel,
            #'created_at': self.created_at.isoformat() if self.created_at else None,
            #'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 