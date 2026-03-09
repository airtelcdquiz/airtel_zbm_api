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

@user_bp.route('/api/users/<int:phone_number>', methods=['GET'])
@AuthController.token_required
def get_user(current_user, phone_number):
    return UserController.get_user(phone_number) 


@user_bp.route('/api/users/<int:phone_number>/permissions', methods=['GET'])
@AuthController.token_required
def get_user_permissions(current_user, phone_number):
    return UserController.get_user_permissions(phone_number)

@user_bp.route('/api/users/<int:phone_number>/roles', methods=['GET'])
@AuthController.token_required
def get_user_roles(current_user, phone_number):
    return UserController.get_user_roles(phone_number)

@user_bp.route('/api/users/<int:phone_number>/permissions/<int:permission_id>', methods=['POST'])
@AuthController.token_required
def add_permission_to_user(current_user, phone_number, permission_id):
    return UserController.add_permission(phone_number, permission_id)

@user_bp.route('/api/users/<int:phone_number>/permissions/<int:permission_id>', methods=['DELETE'])
@AuthController.token_required
def remove_permission_from_user(current_user, phone_number, permission_id):
    return UserController.remove_permission(phone_number, permission_id)

@user_bp.route('/api/users/<int:phone_number>/roles/<int:role_id>', methods=['POST'])
@AuthController.token_required
def add_role_to_user(current_user, phone_number, role_id):
    return UserController.add_role(phone_number, role_id)

@user_bp.route('/api/users/<int:phone_number>/roles/<int:role_id>', methods=['DELETE'])
@AuthController.token_required
def remove_role_from_user(current_user, phone_number, role_id):
    return UserController.remove_role(phone_number, role_id)

@user_bp.route('/api/users/<int:phone_number>/set_superuser', methods=['POST'])
@AuthController.token_required
def set_superuser(current_user, phone_number):
    return UserController.set_superuser(phone_number)

@user_bp.route('/api/users/<int:phone_number>/unset_superuser', methods=['POST'])
@AuthController.token_required
def unset_superuser(current_user, phone_number):
    return UserController.unset_superuser(phone_number)

@user_bp.route('/api/users/<int:phone_number>/activate', methods=['POST'])
@AuthController.token_required
def activate_user(current_user, phone_number):
    return UserController.activate_user(phone_number)

@user_bp.route('/api/users/<int:phone_number>/deactivate', methods=['POST'])
@AuthController.token_required
def deactivate_user(current_user, phone_number):
    return UserController.deactivate_user(phone_number)
