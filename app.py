from flask import Flask

from flask_cors import CORS 
from config.config import Config
from models.user import db
from routes.user_routes import user_bp
from routes.school_routes import school_bp
from routes.auth_routes import auth_bp
from routes.role_routes import role_bp
from routes.permission_routes import permission_bp
from routes.campaigns_question_routes import campaigns_question_bp
from routes.statistics_routes import statistics_bp
from routes.document_routes import document_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config.from_object(Config)
    
    # Initialisation de la base de données
    db.init_app(app)
    
    # Enregistrement des blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(campaigns_question_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(document_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )