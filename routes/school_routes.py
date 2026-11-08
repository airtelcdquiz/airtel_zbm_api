from flask import Blueprint
from controllers.school_controller import SchoolController
from controllers.auth_controller import AuthController
from utils.access import superuser_required, can_access_school
from flask import jsonify

school_bp = Blueprint('schools', __name__)

@school_bp.route('/api/schools', methods=['GET'])
@AuthController.token_required
def get_schools(current_user):
    return SchoolController.get_all_schools(current_user)

@school_bp.route('/api/schools', methods=['POST'])
@AuthController.token_required
@superuser_required
def create_school(current_user):
    return SchoolController.create_school()

@school_bp.route('/api/schools/<code>', methods=['GET'])
@AuthController.token_required
def get_school(current_user, code):
    if not can_access_school(current_user, code):
        return jsonify({'error': 'Not found'}), 404
    return SchoolController.get_school(code)

@school_bp.route('/api/schools/<code>', methods=['PUT'])
@AuthController.token_required
@superuser_required
def update_school(current_user, code):
    return SchoolController.update_school(code)

@school_bp.route('/api/schools/<code>', methods=['DELETE'])
@AuthController.token_required
@superuser_required
def delete_school(current_user, code):
    return SchoolController.delete_school(code) 