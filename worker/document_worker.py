from celery import Celery, chain
from celery.signals import task_success, task_failure, worker_ready
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
from sqlalchemy import or_
 
from google import genai

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('document_worker')

# Configuration Celery
celery = Celery('document_worker',
                broker=os.getenv('REDIS_URL', 'redis://ussd-redis:6379'),
                backend=os.getenv('REDIS_URL', 'redis://ussd-redis:6379'))

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ussd:ussd@ussd-postgres/ussd')
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
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA7QsUL_RdNW2Eq3bP5oQr6ZimvWaMGa04')
GEMINI_API_URL = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3-flash-preview')
MAX_RETRIES = os.getenv('MAX_RETRIES', 3)
RETRY_DELAY = os.getenv('RETRY_DELAY', 300)  # 5 minutes en secondes
COUNTDOWN = os.getenv('COUNTDOWN', 10)
COUNTDOWN_RETRYDOC = os.getenv('COUNTDOWN_RETRYDOC', 10)

client = genai.Client(api_key=GEMINI_API_KEY)

OLLAMA_URL = os.getenv("OLLAMA_URL", "https://ollama.saas.cd/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def generate_questions_from_text_ollama(page_text):
    logger.info("Début de la génération des questions avec Ollama")

    prompt = f"""
    Tu es un assistant éducatif.

    Génère au moins 50 questions à choix multiples de culture générale sur la RDC
    basées uniquement sur ce texte :

    {page_text}

    Pour chaque question retourne un JSON avec :
    - question
    - assertions (4 options)
    - reponse (index de la bonne réponse)

    Répond uniquement avec un seul tableau JSON contenant les objets des questons comme ceci :

    [
        {{"question": "...", "assertions": ["...", "...", "...", "..."], "reponse": 2}},
        {{"question": "...", "assertions": ["...", "...", "...", "..."], "reponse": 4}}
    ]
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        logger.info(f"Ollama response : {response.text}")
        if response.status_code != 200:
            logger.error(f"Ollama error {response.status_code}")
            logger.error(response.text)
            return None

        data = response.json()
        content = data.get("response", "")

        content = content.replace("```json", "").replace("```", "").strip()

        logger.info(content)
        questions = json.loads(content)

        logger.info(f"{len(questions)} questions générées")
        return questions

    except Exception as e:
        logger.error(f"Erreur Ollama: {str(e)}")
        logger.error(traceback.format_exc())
        return None

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
                return None
        else:
            logger.error(f"Erreur API Gemini - Status: {response.status_code}")
            logger.error(f"Réponse d'erreur: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'appel à Gemini: {str(e)}")
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        return None

def generate_questions_from_text_new(page_text):
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
  {{"question": "...", "assertions": ["...", "...", "...", "..."], "reponse": 2}}
]
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        content = response.text
        content = content.replace("```json", "").replace("```", "")

        questions = json.loads(content)

        logger.info(f"{len(questions)} questions générées")
        return questions

    except Exception as e:
        logger.error(f"Erreur Gemini: {str(e)}")
        logger.error(traceback.format_exc())
        return None

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
            self.retry(countdown=COUNTDOWN_RETRYDOC)
            return
        
        # Récupérer le document
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.processing_status != 'processing'
        ).with_for_update().first()
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
                    questions = generate_questions_from_text_ollama(text)

                    if questions != None :
                    
                        # Sauvegarder les questions dans la base de données
                        logger.info(f"Sauvegarde de {len(questions)} questions pour la page {i+1}")
                        for q in questions:
                            try:
                                campaign_question = CampaignsQuestion(
                                    question=q['question'],
                                    option_1=q['assertions'][0],
                                    option_2=q['assertions'][1],
                                    option_3=q['assertions'][2],
                                    option_4=q['assertions'][3],
                                    response=q['reponse'] + 1,
                                    # campaign_question_type='special-question',
                                    #campaign_status='0',
                                    #counter='0',
                                    #presenter='0',
                                    is_active=False
                                )
                                db.add(campaign_question)
                                total_questions += 1
                            except Exception as quest_error:
                                logger.error(f"Erreur lors du traitement d'une question sur la page {i+1}: {str(quest_error)}")
                                continue
                        
                        document.current_page = i + 1
                        db.commit()
                        logger.info(f"Page {i+1} traitée avec succès")
                    else:
                        logger.info('questions == None')
                        continue
                except Exception as page_error:
                    error_msg = f"Erreur sur la page {i+1}: {str(page_error)}"
                    logger.error(error_msg)
                    logger.error(f"Stacktrace: {traceback.format_exc()}")
                    # On continue avec la page suivante au lieu de lever l'exception
                    document.current_page = i + 1
                    document.processing_result = {
                        'error_page': i + 1,
                        'error_details': str(page_error),
                        'stack_trace': traceback.format_exc(),
                        'total_questions_generated': total_questions
                    }
                    db.commit()
                    continue
            
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
            
            # Vérifier s'il y a d'autres documents en attente
            check_pending_documents.delay()
            
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

@celery.task(name='check_pending_documents')
def check_pending_documents():
    """Vérifie s'il y a des documents en attente ou en échec et les traite"""
    logger.info("Vérification des documents en attente et en échec")
    db = SessionLocal()
    try:
        # Vérifier s'il y a un document en cours de traitement
        processing_doc = db.query(Document).filter(
            Document.processing_status == 'processing'
        ).first()
        
        if processing_doc:
            logger.info(f"Un document ({processing_doc.id}) est déjà en cours de traitement")
            return
        
        # Chercher le prochain document en attente
        pending_doc = db.query(Document).filter(
            Document.processing_status == 'pending'
        ).order_by(Document.created_at.asc()).first()
        
        if pending_doc:
            logger.info(f"Lancement du traitement du document en attente {pending_doc.id}")
            process_document.delay(pending_doc.id)
            return
            
        # Si aucun document en attente, vérifier les documents en échec
        failed_docs = db.query(Document).filter(
            Document.processing_status == 'failed',
            Document.retry_count < MAX_RETRIES,
            or_(
                Document.last_retry_at == None,
                Document.last_retry_at < datetime.utcnow() - timedelta(seconds=RETRY_DELAY)
            )
        ).order_by(Document.created_at.asc()).all()
        
        if failed_docs:
            logger.info(f"Trouvé {len(failed_docs)} documents en échec à retenter")
            for doc in failed_docs:
                logger.info(f"Relancement du traitement du document en échec {doc.id}")
                process_document.delay(doc.id)
        else:
            logger.info("Aucun document en attente ou en échec à traiter")
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des documents: {str(e)}")
        logger.error(f"Stacktrace: {traceback.format_exc()}")
    finally:
        db.close()
        
@celery.task(name='check_processing_documents')
def check_processing_documents():
    """Vérifie s'il y a des documents en cours de traitement au démarrage du worker"""
    logger.info("Vérification des documents en cours de traitement au démarrage")
    db = SessionLocal()
    try:
        # Chercher les documents en cours de traitement
        processing_docs = db.query(Document).filter(
            Document.processing_status == 'processing'
        ).all()
        
        for doc in processing_docs:
            logger.info(f"Reprise du traitement du document {doc.id}")
            process_document.delay(doc.id)

        # Chercher le prochain document en attente
        pending_doc = db.query(Document).filter(
            Document.processing_status == 'pending'
        ).order_by(Document.created_at.asc()).first()
        
        if pending_doc:
            logger.info(f"Lancement du traitement du document en attente {pending_doc.id}")
            process_document.delay(pending_doc.id)
            return
            
        # Si aucun document en attente, vérifier les documents en échec
        failed_docs = db.query(Document).filter(
            Document.processing_status == 'failed',
            Document.retry_count < MAX_RETRIES,
            or_(
                Document.last_retry_at == None,
                Document.last_retry_at < datetime.utcnow() - timedelta(seconds=RETRY_DELAY)
            )
        ).order_by(Document.created_at.asc()).all()
        
        if failed_docs:
            logger.info(f"Trouvé {len(failed_docs)} documents en échec à retenter")
            for doc in failed_docs:
                logger.info(f"Relancement du traitement du document en échec {doc.id}")
                process_document.delay(doc.id)
        else:
            logger.info(f"Aucun document à traiter. Planification d'une nouvelle vérification dans {COUNTDOWN} secondes")
            #check_processing_documents.apply_async(countdown=COUNTDOWN)  # 600 secondes = 10 minutes
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des documents en cours de traitement: {str(e)}")
        logger.error(f"Stacktrace: {traceback.format_exc()}")
    finally:
        db.close()

# Appeler check_processing_documents au démarrage du worker
@worker_ready.connect
def at_start(sender, **kwargs):
    check_processing_documents.delay()

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