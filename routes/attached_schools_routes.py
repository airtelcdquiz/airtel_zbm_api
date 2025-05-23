from flask import Blueprint
from controllers.attached_schools_controller import AttachedSchoolsController
from controllers.auth_controller import AuthController

attached_schools_bp = Blueprint('attached_schools', __name__)


# Get all attached schools
@attached_schools_bp.route('/api/attached-schools', methods=['GET'])
@AuthController.token_required
def get_all_attached_schools(current_user):
    return AttachedSchoolsController.get_all()

# Get user's attached schools
@attached_schools_bp.route('/api/attached-schools/me', methods=['GET'])
@AuthController.token_required
def get_user_attached_schools(current_user):
    return AttachedSchoolsController.get_user_attached_schools(current_user)

# Get attached school by ID
@attached_schools_bp.route('/api/attached-schools/<int:id>', methods=['GET'])
@AuthController.token_required
def get_attached_school(current_user, id):
    return AttachedSchoolsController.get_by_id(id)

# Create new attached school
@attached_schools_bp.route('/api/attached-schools', methods=['POST'])
@AuthController.token_required
def create_attached_school(current_user):
    return AttachedSchoolsController.create()

# Update attached school
@attached_schools_bp.route('/api/attached-schools/<int:id>', methods=['PUT'])
@AuthController.token_required
def update_attached_school(current_user, id):
    return AttachedSchoolsController.update(id)

# Delete attached school
@attached_schools_bp.route('/api/attached-schools/<int:id>', methods=['DELETE'])
@AuthController.token_required
def delete_attached_school(current_user, id):
    return AttachedSchoolsController.delete(id)