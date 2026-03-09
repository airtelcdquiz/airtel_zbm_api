from flask import Blueprint
from controllers.school_controller import SchoolController
from controllers.auth_controller import AuthController

school_bp = Blueprint('schools', __name__)

@school_bp.route('/api/schools', methods=['GET'])
@AuthController.token_required
def get_schools(current_user):
    return SchoolController.get_all_schools()

@school_bp.route('/api/schools', methods=['POST'])
@AuthController.token_required
def create_school(current_user):
    return SchoolController.create_school()

@school_bp.route('/api/schools/<int:code>', methods=['GET'])
@AuthController.token_required
def get_school(current_user, code):
    return SchoolController.get_school(code)

@school_bp.route('/api/schools/<int:code>', methods=['PUT'])
@AuthController.token_required
def update_school(current_user, code):
    return SchoolController.update_school(code)

@school_bp.route('/api/schools/<int:code>', methods=['DELETE'])
@AuthController.token_required
def delete_school(current_user, code):
    return SchoolController.delete_school(code) 