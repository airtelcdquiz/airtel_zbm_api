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