from flask import Blueprint, jsonify
from flask import request
from models.user import User
from controllers.auth_controller import AuthController
import jwt
import logging

logger = logging.getLogger(__name__)

def get_user_by_auth():
    token = request.headers.get('Authorization')
    if not token:
        logger.warning("get_user_by_auth: en-tete Authorization manquant")
        return None

    parts = token.split(' ')
    if len(parts) != 2 or parts[0] != 'Bearer':
        logger.warning("get_user_by_auth: en-tete Authorization mal forme")
        return None
    raw_token = parts[1]

    try:
        data = jwt.decode(raw_token, AuthController.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        logger.warning("get_user_by_auth: JWT expire")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("get_user_by_auth: JWT invalide: %s: %s", type(e).__name__, e)
        return None

    try:
        phone_number = data.get('phone_number')
        current_user = User.query.get(phone_number)
        if not current_user:
            logger.warning("get_user_by_auth: aucun utilisateur pour phone_number=%r", phone_number)
            return None
        return current_user
    except Exception:
        # Defaillance inattendue (DB, etc.) : on journalise la stack complete.
        logger.exception("get_user_by_auth: erreur inattendue")
        return None

def get_user_permissions():
    current_user = get_user_by_auth()
    if not current_user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Récupérer toutes les permissions
    all_permissions = current_user.get_all_permissions()
    
    # Récupérer les rôles et leurs permissions
    roles = [{
        'name': role.name,
        'permissions': [p.name for p in role.permissions]
    } for role in current_user.roles]
    
    # Récupérer les permissions directes
    direct_permissions = [p.name for p in current_user.direct_permissions]

    return jsonify({
        'permissions': all_permissions,
        'roles': roles,
        'direct_permissions': direct_permissions,
        'is_superuser': current_user.is_superuser
    })