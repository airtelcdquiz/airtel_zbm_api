from flask import Blueprint
from controllers.role_controller import RoleController
from controllers.auth_controller import AuthController
from utils.access import superuser_required

role_bp = Blueprint('roles', __name__)

# Routes pour les rôles
@role_bp.route('/api/roles', methods=['GET'])
@AuthController.token_required
def get_roles(current_user):
    return RoleController.get_all()

@role_bp.route('/api/roles/<int:role_id>', methods=['GET'])
@AuthController.token_required
def get_role(current_user, role_id):
    return RoleController.get_by_id(role_id)

@role_bp.route('/api/roles', methods=['POST'])
@AuthController.token_required
@superuser_required
def create_role(current_user):
    return RoleController.create()

@role_bp.route('/api/roles/bulk', methods=['POST'])
@AuthController.token_required
@superuser_required
def create_many_roles(current_user):
    return RoleController.create_many()

@role_bp.route('/api/roles/<int:role_id>', methods=['PUT'])
@AuthController.token_required
@superuser_required
def update_role(current_user, role_id):
    return RoleController.update(role_id)

@role_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
@AuthController.token_required
@superuser_required
def delete_role(current_user, role_id):
    return RoleController.delete(role_id)

@role_bp.route('/api/roles/<int:role_id>/permissions/<int:permission_id>', methods=['POST'])
@AuthController.token_required
@superuser_required
def add_permission_to_role(current_user, role_id, permission_id):
    return RoleController.add_permission(role_id, permission_id)

@role_bp.route('/api/roles/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
@AuthController.token_required
@superuser_required
def remove_permission_from_role(current_user, role_id, permission_id):
    return RoleController.remove_permission(role_id, permission_id) 