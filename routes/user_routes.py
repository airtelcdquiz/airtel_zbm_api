from flask import Blueprint
from controllers.user_controller import UserController
from controllers.auth_controller import AuthController

user_bp = Blueprint('users', __name__)

@user_bp.route('/api/users', methods=['GET'])
@AuthController.token_required
def get_users(current_user):
    return UserController.get_all_users()

@user_bp.route('/api/users', methods=['POST'])
@AuthController.token_required
def create_user(current_user):
    return UserController.create_user()

@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
@AuthController.token_required
def get_user(current_user, user_id):
    return UserController.get_user(user_id) 


@user_bp.route('/api/users/<int:user_id>/permissions', methods=['GET'])
@AuthController.token_required
def get_user_permissions(current_user, user_id):
    return UserController.get_user_permissions(user_id)

@user_bp.route('/api/users/<int:user_id>/roles', methods=['GET'])
@AuthController.token_required
def get_user_roles(current_user, user_id):
    return UserController.get_user_roles(user_id)

@user_bp.route('/api/users/<int:user_id>/permissions/<int:permission_id>', methods=['POST'])
@AuthController.token_required
def add_permission_to_user(current_user, user_id, permission_id):
    return UserController.add_permission(user_id, permission_id)

@user_bp.route('/api/users/<int:user_id>/permissions/<int:permission_id>', methods=['DELETE'])
@AuthController.token_required
def remove_permission_from_user(current_user, user_id, permission_id):
    return UserController.remove_permission(user_id, permission_id)

@user_bp.route('/api/users/<int:user_id>/roles/<int:role_id>', methods=['POST'])
@AuthController.token_required
def add_role_to_user(current_user, user_id, role_id):
    return UserController.add_role(user_id, role_id)

@user_bp.route('/api/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@AuthController.token_required
def remove_role_from_user(current_user, user_id, role_id):
    return UserController.remove_role(user_id, role_id)

@user_bp.route('/api/users/<int:user_id>/set_superuser', methods=['POST'])
@AuthController.token_required
def set_superuser(current_user, user_id):
    return UserController.set_superuser(user_id)

@user_bp.route('/api/users/<int:user_id>/unset_superuser', methods=['POST'])
@AuthController.token_required
def unset_superuser(current_user, user_id):
    return UserController.unset_superuser(user_id)
