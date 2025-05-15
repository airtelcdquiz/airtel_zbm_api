from celery import Celery, chain
from celery.signals import task_success, task_failure
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime, timedelta
from models.document import Document
from models.campaigns_question import CampaignsQuestion
import fitz  # PyMuPDF
import json
import requests
import traceback
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('document_worker')

# Configuration Celery
celery = Celery('document_worker',
                broker=os.getenv('REDIS_URL', 'redis://41.243.25.144:6379'),
                backend=os.getenv('REDIS_URL', 'redis://41.243.25.144:6379'))

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql://trivia_user:Adm!n2024$@41.243.25.144/airtel_trivia_test_backup')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Configuration pour le traitement séquentiel
celery.conf.update(
    task_acks_late=True,  # Ne pas acquitter la tâche avant qu'elle ne soit terminée
    worker_prefetch_multiplier=1,  # Ne prendre qu'une tâche à la fois
    task_default_queue='document_processing',  # File d'attente dédiée
    task_default_routing_key='document_processing',
    task_default_exchange='document_processing'
)

# Configuration Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAayNaBCTKcDYhWYMpR5He_7Ru61IMlIyI')
GEMINI_API_URL = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent')

MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 minutes en secondes

def generate_questions_from_text(page_text):
    logger.info("Début de la génération des questions avec Gemini")
    prompt = f"""
Tu es un assistant éducatif. Génère au moins 50 questions à choix multiples de culture générale sur la RDC basées uniquement sur ce texte :

{page_text}

Pour chaque question, retourne un objet JSON avec :
- question
- assertions (4 options)
- reponse (index de la bonne réponse)

Répond uniquement avec un tableau JSON comme :
[
  {{"question": "...", "assertions": ["...", "...", "...", "..."], "reponse": 2}},
  ...
]
"""

    try:
        logger.debug(f"Envoi de la requête à l'API Gemini avec un texte de {len(page_text)} caractères")
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )

        if response.status_code == 200:
            try:
                content = response.json()['candidates'][0]['content']['parts'][0]['text']
                content = content.replace('```json', '').replace('```', '')
                questions = json.loads(content)
                logger.info(f"Questions générées avec succès: {len(questions)} questions")
                return questions
            except Exception as e:
                logger.error(f"Erreur lors du parsing de la réponse Gemini: {str(e)}")
                logger.error(f"Réponse brute: {response.text}")
                logger.error(f"Stacktrace: {traceback.format_exc()}")
                return []
        else:
            logger.error(f"Erreur API Gemini - Status: {response.status_code}")
            logger.error(f"Réponse d'erreur: {response.text}")
            return []
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel à Gemini: {str(e)}")
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return []

@celery.task(bind=True, name='process_document')
def process_document(self, document_id):
    """Traitement d'un document en arrière-plan"""
    logger.info(f"Début du traitement du document {document_id}")
    db = SessionLocal()
    document = None
    try:
        # Vérifier si un autre document est en cours de traitement
        processing_doc = db.query(Document).filter(
            Document.processing_status == 'processing'
        ).first()
        
        if processing_doc and processing_doc.id != document_id:
            logger.warning(f"Un autre document ({processing_doc.id}) est en cours de traitement")
            self.retry(countdown=30)
            return
        
        # Récupérer le document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            error_msg = f"Document {document_id} non trouvé"
            logger.error(error_msg)
            raise Exception(error_msg)

        # Vérifier si on doit réessayer après un échec
        if document.processing_status == 'failed':
            logger.info(f"Tentative de reprise après échec - Essai n°{document.retry_count + 1}")
            if document.retry_count >= MAX_RETRIES:
                error_msg = f"Nombre maximum de tentatives ({MAX_RETRIES}) atteint"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            if document.last_retry_at and (datetime.utcnow() - document.last_retry_at) < timedelta(seconds=RETRY_DELAY):
                logger.info(f"Délai de reprise non atteint, report du traitement")
                self.retry(countdown=RETRY_DELAY)
                return
        
        # Mettre à jour le compteur de tentatives
        document.retry_count += 1
        document.last_retry_at = datetime.utcnow()
        
        # Marquer le document comme en cours de traitement
        document.processing_status = 'processing'
        db.commit()
        
        # Traitement du PDF
        logger.info(f"Ouverture du fichier PDF: {document.file_path}")
        doc = fitz.open(document.file_path)
        total_questions = 0
        start_page = document.current_page if document.current_page else 0
        document.total_pages = len(doc)
        logger.info(f"Document de {document.total_pages} pages, début à la page {start_page}")
        
        try:
            for i, page in enumerate(doc[start_page:], start=start_page):
                try:
                    text = page.get_text()
                    if len(text.strip()) < 100:
                        logger.info(f"Page {i+1} ignorée car trop peu de texte")
                        continue

                    logger.info(f"Traitement de la page {i+1}/{document.total_pages}")
                    questions = generate_questions_from_text(text)
                    
                    # Sauvegarder les questions dans la base de données
                    logger.info(f"Sauvegarde de {len(questions)} questions pour la page {i+1}")
                    for q in questions:
                        campaign_question = CampaignsQuestion(
                            campaign_question=q['question'],
                            campaign_value1=q['assertions'][0],
                            campaign_value2=q['assertions'][1],
                            campaign_value3=q['assertions'][2],
                            campaign_value4=q['assertions'][3],
                            campaign_answer=q['reponse'] + 1,
                            campaign_question_type='special-question',
                            campaign_status='0',
                            counter='0',
                            presenter='0',
                            is_active=False
                        )
                        db.add(campaign_question)
                        total_questions += 1
                    
                    document.current_page = i + 1
                    db.commit()
                    logger.info(f"Page {i+1} traitée avec succès")
                    
                except Exception as page_error:
                    error_msg = f"Erreur sur la page {i+1}: {str(page_error)}"
                    logger.error(error_msg)
                    logger.error(f"Stacktrace: {traceback.format_exc()}")
                    document.processing_status = 'failed'
                    document.processing_error = error_msg
                    document.processing_result = {
                        'error_page': i + 1,
                        'error_details': str(page_error),
                        'stack_trace': traceback.format_exc(),
                        'total_questions_generated': total_questions
                    }
                    db.commit()
                    raise
            
            # Traitement réussi
            logger.info(f"Traitement terminé avec succès: {total_questions} questions générées")
            document.processed_at = datetime.now()
            document.processing_status = 'completed'
            document.processing_result = {
                'total_questions': total_questions,
                'total_pages_processed': document.total_pages,
                'completion_time': datetime.utcnow().isoformat()
            }
            db.commit()
            
            return {
                'status': 'success',
                'document_id': document_id,
                'total_questions': total_questions
            }
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement du document: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Stacktrace: {traceback.format_exc()}")
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.processing_result = {
                'error_details': str(e),
                'stack_trace': traceback.format_exc(),
                'total_questions_generated': total_questions,
                'last_processed_page': document.current_page
            }
            db.commit()
            raise
            
    except Exception as e:
        error_msg = f"Erreur critique lors du traitement du document: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        if document:
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.processing_result = {
                'error_details': str(e),
                'stack_trace': traceback.format_exc(),
                'last_processed_page': document.current_page if document else None
            }
            db.commit()
        raise
    finally:
        db.close()
        logger.info("Session de base de données fermée")

@task_success.connect
def task_success_handler(sender=None, **kwargs):
    """Gestionnaire appelé quand une tâche réussit"""
    if sender.name == 'process_document':
        logger.info(f"Document {kwargs['result']['document_id']} traité avec succès")
        logger.info(f"Total des questions générées: {kwargs['result']['total_questions']}")

@task_failure.connect
def task_failure_handler(sender=None, **kwargs):
    """Gestionnaire appelé quand une tâche échoue"""
    if sender.name == 'process_document':
        logger.error(f"ÉCHEC DU TRAITEMENT DU DOCUMENT")
        logger.error(f"Exception: {kwargs['exc']}")
        logger.error(f"Traceback complet:")
        logger.error(traceback.format_exc())