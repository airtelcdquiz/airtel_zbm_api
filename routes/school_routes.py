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

@school_bp.route('/api/schools/<int:school_id>', methods=['GET'])
@AuthController.token_required
def get_school(current_user, school_id):
    return SchoolController.get_school(school_id)

@school_bp.route('/api/schools/<int:school_id>', methods=['PUT'])
@AuthController.token_required
def update_school(current_user, school_id):
    return SchoolController.update_school(school_id)

@school_bp.route('/api/schools/<int:school_id>', methods=['DELETE'])
@AuthController.token_required
def delete_school(current_user, school_id):
    return SchoolController.delete_school(school_id) 