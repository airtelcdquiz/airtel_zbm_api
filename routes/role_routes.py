from flask import Blueprint
from controllers.role_controller import RoleController

role_bp = Blueprint('roles', __name__)

# Routes pour les rôles
@role_bp.route('/api/roles', methods=['GET'])
def get_roles():
    return RoleController.get_all()

@role_bp.route('/api/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    return RoleController.get_by_id(role_id)

@role_bp.route('/api/roles', methods=['POST'])
def create_role():
    return RoleController.create()

@role_bp.route('/api/roles/bulk', methods=['POST'])
def create_many_roles():
    return RoleController.create_many()

@role_bp.route('/api/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    return RoleController.update(role_id)

@role_bp.route('/api/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    return RoleController.delete(role_id)

@role_bp.route('/api/roles/<int:role_id>/permissions/<int:permission_id>', methods=['POST'])
def add_permission_to_role(role_id, permission_id):
    return RoleController.add_permission(role_id, permission_id)

@role_bp.route('/api/roles/<int:role_id>/permissions/<int:permission_id>', methods=['DELETE'])
def remove_permission_from_role(role_id, permission_id):
    return RoleController.remove_permission(role_id, permission_id) 