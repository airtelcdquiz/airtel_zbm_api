from flask import Blueprint, jsonify
from flask import request
from models.user import User
from controllers.auth_controller import AuthController
import jwt

def get_user_by_auth():
    token = request.headers.get('Authorization')
    if not token:
        return None

    try:
        token = token.split(' ')[1]  # Enlever le préfixe 'Bearer '
        data = jwt.decode(token, AuthController.SECRET_KEY, algorithms=['HS256'])
        current_user = User.query.get(data['user_id'])
        if not current_user:
            return None
        return current_user
    except Exception:
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