from flask import Blueprint
from controllers.school_controller import SchoolController

school_bp = Blueprint('schools', __name__)

@school_bp.route('/api/schools', methods=['GET'])
def get_schools():
    return SchoolController.get_all_schools()

@school_bp.route('/api/schools', methods=['POST'])
def create_school():
    return SchoolController.create_school()

@school_bp.route('/api/schools/<int:school_id>', methods=['GET'])
def get_school(school_id):
    return SchoolController.get_school(school_id)

@school_bp.route('/api/schools/<int:school_id>', methods=['PUT'])
def update_school(school_id):
    return SchoolController.update_school(school_id)

@school_bp.route('/api/schools/<int:school_id>', methods=['DELETE'])
def delete_school(school_id):
    return SchoolController.delete_school(school_id) 