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
  

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('document_worker')


# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ussd:ussd@ussd-postgres/ussd')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# 🔥 variable globale
processing = None

MAX_RETRIES = os.getenv('MAX_RETRIES', 3)
RETRY_DELAY = os.getenv('RETRY_DELAY', 300)  # 5 minutes en secondes
COUNTDOWN = os.getenv('COUNTDOWN', 10)
COUNTDOWN_RETRYDOC = os.getenv('COUNTDOWN_RETRYDOC', 10)

OLLAMA_URL = os.getenv("OLLAMA_URL", "https://ollama.saas.cd/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

def generate_questions_from_text_ollama(page_text):
    logger.info("Début de la génération des questions avec Ollama")

    prompt = f"""
    Tu es un assistant éducatif.

    Génère au moins 10 questions à choix multiples de culture générale sur la RDC
    basées uniquement sur ce texte :

    {page_text}

    Pour chaque question doit toujours retourne un JSON avec :
    - question
    - assertions (4 options) toujours avoir 4 assertions
    - reponse (index de la bonne réponse) doit toujours etre la bonne reponse à fournir situé entre soit 1, 2, 3 ou 4

    Tu es un assistant qui répond STRICTEMENT en JSON.

    RÈGLES OBLIGATOIRES :
    - Répond uniquement avec un tableau JSON valide
    - Ne mets AUCUN texte avant ou après
    - Ne mets PAS d'explication
    - Ne mets PAS de ```json
    - Le premier caractère doit être [
    - Le dernier caractère doit être ]

    Répond uniquement avec un seul tableau JSON contenant les objets des questons comme ceci :
    Tu ne met pas d'autres details dans ta reponse.
    Ta reponse commence directement par [ les objets json {...}, {...} et  fini par ] avec les objets json des questions

    Exemple de reponse : 
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
                "stream": False,
                "format": "json"   # 🔥 TRÈS IMPORTANT
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


def get_next_document(db):
    """Récupère le prochain document à traiter"""

    # 1️⃣ vérifier si un doc est déjà en processing en DB
    doc = db.query(Document).filter(
        Document.processing_status == 'processing'
    ).first()

    if doc:
        return doc

    # 2️⃣ sinon prendre un doc pending ou failed avec retry < 5
    doc = db.query(Document).filter(
        Document.processing_status != 'completed',
        Document.retry_count < 5
    ).order_by(Document.created_at.asc()).first()

    return doc

def process_document_simple(document_id):
    """Traitement d'un document en arrière-plan"""
    logger.info(f"Début du traitement du document {document_id}")
    db = SessionLocal()
    document = None
    try:
        document = db.query(Document).get(document_id)

        if not document :
            return

        print(f"🚀 Traitement document TITLE:{document.name} - ID:{document.id}")

        # Marquer en processing
        document.processing_status = "processing"
        document.retry_count += 1
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


def worker_loop():
    global processing

    print("🟢 Worker démarré")

    while True:
        db = SessionLocal()

        try:
            # 🔍 Si rien en cours
            if processing is None:

                doc = get_next_document(db)

                if doc:
                    print(f"📥 Nouveau document trouvé: {doc.id}")
                    processing = doc.id
                else:
                    print("😴 Aucun document, sleep...")
                    time.sleep(5)
                    continue

        finally:
            db.close()

        # 🔥 Traitement hors session DB
        if processing is not None:
            process_document_simple(processing)

            # reset après traitement
            processing = None


if __name__ == "__main__":
    worker_loop()