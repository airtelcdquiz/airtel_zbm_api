from .database import db
from datetime import datetime

class CampaignsQuestion(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # campaign_code = db.Column(db.String(255), nullable=True, index=True)
    question = db.Column(db.String(255), nullable=True)
    # question_type = db.Column(db.String(255), nullable=False)
    option_1 = db.Column(db.String(255), nullable=True)
    option_2 = db.Column(db.String(255), nullable=True)
    option_3 = db.Column(db.String(255), nullable=True)
    option_4 = db.Column(db.String(255), nullable=True)
    response = db.Column(db.String(255), nullable=True)
    #campaign_status = db.Column(db.Enum('0', '1', '2', '3', '4', name='campaign_status_enum'), nullable=False, default='0')
    #counter = db.Column(db.String(255), nullable=False)
    #presenter = db.Column(db.Enum('0', '1', name='presenter_enum'), nullable=False, default='0')
    #date = db.Column(db.TIMESTAMP, nullable=False, server_default=db.text('CURRENT_TIMESTAMP'))
    #created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    archived = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            # 'campaign_code': self.campaign_code,
            'question': self.question,
            # 'question_type': self.question_type,
            'option_1': self.option_1,
            'option_2': self.option_2,
            'option_3': self.option_3,
            'option_4': self.option_4,
            'response': self.response,
            #'campaign_status': self.campaign_status,
            #'counter': self.counter,
            #'presenter': self.presenter,
            #'date': self.date.isoformat() if self.date else None,
            #'created_at': self.created_at.isoformat() if self.created_at else None,
            #'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'archived': self.archived
        } 