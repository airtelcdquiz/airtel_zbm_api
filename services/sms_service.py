import random
import string
import os
import requests
from dotenv import load_dotenv
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class SMSService:
    def __init__(self):
        self.sms_api_url = os.getenv('SMS_API_URL', 'https://sms-worker-api.airtelquiz.com/send-sms')
        logger.info(f"Service SMS initialisé avec l'API URL: {self.sms_api_url}")

    def generate_otp(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    def send_otp(self, phone_number, otp, callback=None):
        """
        Envoie un SMS via l'API Express
        """
        try:
            # Préparer le message
            message = f"Votre code OTP est: {otp}"
            
            # Préparer les données pour l'API
            data = {
                'phoneNumber': phone_number,
                'message': message
            }

            # Envoyer la requête à l'API
            response = requests.post(self.sms_api_url, json=data)
            print(response)
            print(response.status_code)
            print(response.text)
            if response.status_code == 200:
                logger.info(f"SMS ajouté à la file d'attente pour {phone_number}")
                if callback:
                    callback(True)
                return True
            else:
                logger.error(f"Erreur API SMS: {response.text}")
                if callback:
                    callback(False)
                return False

        except Exception as e:
            print(e)
            logger.error(f"Erreur lors de l'envoi du SMS: {str(e)}")
            if callback:
                callback(False)
            return False