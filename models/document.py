from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .database import db 
from .user import User

class Document(db.Model):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer)  # Taille en bytes
    mime_type = Column(String(100), default='application/pdf')
    uploaded_by = Column(String(255), ForeignKey('users.phone_number'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Champs pour le suivi du traitement
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    processed_at = Column(DateTime)
    processing_error = Column(Text)
    current_page = Column(Integer, default=0)  # Page en cours de traitement
    total_pages = Column(Integer)  # Nombre total de pages
    retry_count = Column(Integer, default=0)  # Nombre de tentatives
    last_retry_at = Column(DateTime)  # Dernière tentative
    processing_result = Column(JSON)  # Résultats détaillés du traitement

    # Relations
    user = relationship(User, backref='documents', foreign_keys=[uploaded_by])

    def __repr__(self):
        return f'<Document {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'processing_status': self.processing_status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_error': self.processing_error,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'retry_count': self.retry_count,
            'last_retry_at': self.last_retry_at.isoformat() if self.last_retry_at else None,
            'processing_result': self.processing_result
        } 