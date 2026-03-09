import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://ussd:ussd@ussd-postgres/ussd')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000 