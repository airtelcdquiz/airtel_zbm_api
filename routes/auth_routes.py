from flask import Blueprint
from controllers.auth_controller import AuthController
from routes.auth import get_user_permissions
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    return AuthController.send_otp()

@auth_bp.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    return AuthController.verify_otp()/send-otp

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return AuthController.logout()

@auth_bp.route('/api/auth/check-session', methods=['GET'])
def check_session():
    return AuthController.check_session()

@auth_bp.route('/api/me/permissions', methods=['GET'])
def get_permissions():
    return get_user_permissions()