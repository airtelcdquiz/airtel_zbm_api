from flask import Blueprint
from controllers.user_controller import UserController

user_bp = Blueprint('users', __name__)

@user_bp.route('/api/users', methods=['GET'])
def get_users():
    return UserController.get_all_users()

@user_bp.route('/api/users', methods=['POST'])
def create_user():
    return UserController.create_user()

@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return UserController.get_user(user_id) 