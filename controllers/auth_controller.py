from flask import jsonify, request
from datetime import datetime, timedelta
import os
import jwt
from models.user import User, db
from models.otp import OTP
from models.session import Session
from services.sms_service import SMSService
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class AuthController:
    # Signe ET vérifie les JWT de session (generate_token / check_session /
    # get_user_by_auth). La valeur vient de l'environnement (injectée par le
    # docker-compose, qui l'interpole depuis Dokploy) ; `or` fait retomber
    # sur la valeur historique si la variable est absente OU vide (p. ex.
    # interpolation non résolue), pour ne jamais signer avec une clé vide.
    SECRET_KEY = os.getenv('JWT_SECRET') or 'votre_cle_secrete_jwt'
    sms_service = SMSService()

    @staticmethod
    def generate_token(phone_number):
        payload = {
            'phone_number': phone_number,
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
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Générer l'OTP
        otp_code = AuthController.sms_service.generate_otp()
        otp = OTP(phone_number=phone_number, otp=otp_code)
        
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
            phone_number=phone_number,
            otp=otp_code,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()

        if not otp :
            return jsonify({'error': 'OTP non trouvé'}), 400

        if not otp.is_valid():
            return jsonify({'error': 'OTP invalide ou expiré'}), 400

        # Marquer l'OTP comme utilisé
        otp.is_used = True
        db.session.commit()

        # Vérifier si l'utilisateur existe et est actif
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        if not user.is_active:
            return jsonify({'error': 'Compte utilisateur désactivé'}), 403

        # Générer le token JWT
        token = AuthController.generate_token(user.phone_number)

        # Créer une nouvelle session
        session = Session(token=token, phone_number=user.phone_number)
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
                current_user = User.query.get(data['phone_number'])
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
            logger.warning("check_session: en-tete Authorization manquant")
            return jsonify({'error': 'Token manquant'}), 401

        parts = token.split(' ')
        if len(parts) != 2 or parts[0] != 'Bearer':
            logger.warning("check_session: en-tete Authorization mal forme: %r", token[:30])
            return jsonify({'error': 'Token mal forme'}), 401
        raw_token = parts[1]

        # 1) Validation de la signature / expiration du JWT.
        try:
            data = jwt.decode(raw_token, AuthController.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            logger.warning("check_session: JWT expire") 
            return jsonify({'error': 'Session expiree'}), 401
        except jwt.InvalidSignatureError:
            # Cause classique : le token a ete signe avec une autre valeur de
            # JWT_SECRET (ancien cookie, ou cle Dokploy differente).
            logger.warning("check_session: signature JWT invalide (JWT_SECRET different ?)")
            return jsonify({'error': 'Session invalide'}), 401
        except jwt.InvalidTokenError as e:
            logger.warning("check_session: JWT invalide: %s: %s", type(e).__name__, e)
            return jsonify({'error': 'Session invalide'}), 401

        # 2) Verification en base (utilisateur + session).
        try:
            phone_number = data.get('phone_number')
            current_user = User.query.get(phone_number)
            if not current_user:
                logger.warning("check_session: aucun utilisateur pour phone_number=%r", phone_number)
                return jsonify({'error': 'Utilisateur non trouve'}), 401

            session = Session.query.filter_by(token=raw_token).first()
            if not session:
                logger.warning("check_session: aucune session en base pour ce token (user=%s)", phone_number)
                return jsonify({'error': 'Session invalide ou expiree'}), 401
            if not session.is_valid():
                logger.warning("check_session: session expiree en base (user=%s, expire_at=%s)", phone_number, session.expire_at)
                return jsonify({'error': 'Session invalide ou expiree'}), 401

            return jsonify({
                'valid': True,
                'user': current_user.to_dict()
            }), 200

        except Exception:
            # Vraie defaillance serveur (DB, serialisation...). On loggue la
            # stack complete et on renvoie 500 : cote dashboard, un 5xx affiche
            # une erreur au lieu de rediriger vers /login (pas de boucle).
            logger.exception("check_session: erreur inattendue")
            return jsonify({'error': 'Erreur interne'}), 500
