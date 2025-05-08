import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://user:password@localhost/dbname')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000 