from flask import Blueprint
from controllers.permission_controller import PermissionController
from controllers.auth_controller import AuthController
from utils.access import superuser_required

permission_bp = Blueprint('permissions', __name__)

# Routes pour les permissions
@permission_bp.route('/api/permissions', methods=['GET'])
@AuthController.token_required
def get_permissions(current_user):
    return PermissionController.get_all()

@permission_bp.route('/api/permissions/<int:permission_id>', methods=['GET'])
@AuthController.token_required
def get_permission(current_user, permission_id):
    return PermissionController.get_by_id(permission_id)

@permission_bp.route('/api/permissions', methods=['POST'])
@AuthController.token_required
@superuser_required
def create_permission(current_user):
    return PermissionController.create()

@permission_bp.route('/api/permissions/bulk', methods=['POST'])
@AuthController.token_required
@superuser_required
def create_many_permissions(current_user):
    return PermissionController.create_many()

@permission_bp.route('/api/permissions/<int:permission_id>', methods=['PUT'])
@AuthController.token_required
@superuser_required
def update_permission(current_user, permission_id):
    return PermissionController.update(permission_id)

@permission_bp.route('/api/permissions/<int:permission_id>', methods=['DELETE'])
@AuthController.token_required
@superuser_required
def delete_permission(current_user, permission_id):
    return PermissionController.delete(permission_id) 