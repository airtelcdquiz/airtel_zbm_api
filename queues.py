import os
from dotenv import load_dotenv
from bullmq import Queue
import logging
from typing import Union, Dict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Configuration Redis
REDIS_HOST = os.getenv('REDIS_HOST', '41.243.25.144')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASS', '')

# Configuration des files d'attente
redis_config: Dict[str, Union[str, int]] = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'password': REDIS_PASSWORD
}

# Création des files d'attente
bulk_sms_queue = Queue('bulksms', connection=redis_config)
bulk_questions_queue = Queue('bulkQuestions', connection=redis_config)

logger.info(f"Files d'attente initialisées avec Redis sur {REDIS_HOST}:{REDIS_PORT}") 