from api import create_app, db
from config.config import Config

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Création des tables
        db.create_all()
    
    # Lancement de l'application
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 