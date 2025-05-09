from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/me/permissions', methods=['GET'])
@jwt_required()
def get_user_permissions():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Récupérer toutes les permissions
    all_permissions = user.get_all_permissions()
    
    # Récupérer les rôles et leurs permissions
    roles = [{
        'name': role.name,
        'permissions': [p.name for p in role.permissions]
    } for role in user.roles]
    
    # Récupérer les permissions directes
    direct_permissions = [p.name for p in user.direct_permissions]

    return jsonify({
        'permissions': all_permissions,
        'roles': roles,
        'direct_permissions': direct_permissions,
        'is_superuser': user.is_superuser
    }) 