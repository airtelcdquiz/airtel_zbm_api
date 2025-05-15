from flask import Blueprint
from controllers.permission_controller import PermissionController

permission_bp = Blueprint('permissions', __name__)

# Routes pour les permissions
@permission_bp.route('/api/permissions', methods=['GET'])
def get_permissions():
    return PermissionController.get_all()

@permission_bp.route('/api/permissions/<int:permission_id>', methods=['GET'])
def get_permission(permission_id):
    return PermissionController.get_by_id(permission_id)

@permission_bp.route('/api/permissions', methods=['POST'])
def create_permission():
    return PermissionController.create()

@permission_bp.route('/api/permissions/bulk', methods=['POST'])
def create_many_permissions():
    return PermissionController.create_many()

@permission_bp.route('/api/permissions/<int:permission_id>', methods=['PUT'])
def update_permission(permission_id):
    return PermissionController.update(permission_id)

@permission_bp.route('/api/permissions/<int:permission_id>', methods=['DELETE'])
def delete_permission(permission_id):
    return PermissionController.delete(permission_id) 