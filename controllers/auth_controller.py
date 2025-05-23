from flask import jsonify, request
from datetime import datetime, timedelta
import jwt
from models.user import User, db
from models.otp import OTP
from models.session import Session
from services.sms_service import SMSService
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class AuthController:
    SECRET_KEY = 'votre_cle_secrete_jwt'  # À changer en production
    sms_service = SMSService()

    @staticmethod
    def generate_token(user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)  # Token valide pendant 1 jour
        }
        return jwt.encode(payload, AuthController.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def send_otp():
        data = request.get_json()
        phone_number = data.get('phone_number')

        if not phone_number:
            return jsonify({'error': 'Numéro de téléphone requis'}), 400

        # Vérifier si l'utilisateur existe
        user = User.query.filter_by(participant_phone=phone_number).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Générer l'OTP
        otp_code = AuthController.sms_service.generate_otp()
        otp = OTP(participant_phone=phone_number, otp=otp_code)
        
        try:
            # Sauvegarder l'OTP dans la base de données
            db.session.add(otp)
            db.session.commit()

            # Définir le callback pour gérer le résultat de l'envoi
            def sms_callback(success):
                if not success:
                    logger.error(f"Échec de l'envoi du SMS à {phone_number}")
                    # Ici vous pourriez implémenter une logique de retry ou de notification

            # Envoyer le SMS de manière asynchrone
            AuthController.sms_service.send_otp(phone_number, otp_code, callback=sms_callback)
            
            return jsonify({'message': 'OTP envoyé avec succès'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la génération de l'OTP: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def verify_otp():
        data = request.get_json()
        phone_number = data.get('phone_number')
        otp_code = data.get('otp')

        if not phone_number or not otp_code:
            return jsonify({'error': 'Numéro de téléphone et OTP requis'}), 400

        # Vérifier l'OTP
        otp = OTP.query.filter_by(
            participant_phone=phone_number,
            otp=otp_code,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()

        if not otp or not otp.is_valid():
            return jsonify({'error': 'OTP invalide ou expiré'}), 400

        # Marquer l'OTP comme utilisé
        otp.is_used = True
        db.session.commit()

        # Vérifier si l'utilisateur existe et est actif
        user = User.query.filter_by(participant_phone=phone_number).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        if not user.is_active:
            return jsonify({'error': 'Compte utilisateur désactivé'}), 403

        # Générer le token JWT
        token = AuthController.generate_token(user.id)

        # Créer une nouvelle session
        session = Session(token=token, user_id=user.id)
        db.session.add(session)
        db.session.commit()

        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 200

    @staticmethod
    def logout():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token manquant'}), 401

        try:
            # Supprimer la session de la base de données
            session = Session.query.filter_by(token=token).first()
            if session:
                db.session.delete(session)
                db.session.commit()
            
            return jsonify({'message': 'Déconnexion réussie'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la déconnexion: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Token manquant'}), 401

            try:
                token = token.split(' ')[1]  # Enlever le préfixe 'Bearer '
                data = jwt.decode(token, AuthController.SECRET_KEY, algorithms=['HS256'])
                current_user = User.query.get(data['user_id'])
                if not current_user:
                    return jsonify({'error': 'Utilisateur non trouvé'}), 401
            except Exception as e:
                return jsonify({'error': 'Token invalide'}), 401

            return f(current_user, *args, **kwargs)
        return decorated 

    @staticmethod
    def check_session():
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token manquant'}), 401

        try:
            token = token.split(' ')[1]  # Enlever le préfixe 'Bearer '
            data = jwt.decode(token, AuthController.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 401
                
            # Vérifier si la session existe et est valide
            session = Session.query.filter_by(token=token).first()
            if not session or not session.is_valid():
                return jsonify({'error': 'Session invalide ou expirée'}), 401
                
            return jsonify({
                'valid': True,
                'user': current_user.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Session invalide'}), 401 