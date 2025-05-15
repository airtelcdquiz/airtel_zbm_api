from flask import Blueprint
from controllers.campaigns_question_controller import CampaignsQuestionController
from controllers.auth_controller import AuthController

campaigns_question_bp = Blueprint('campaigns_questions', __name__)

@campaigns_question_bp.route('/api/quiz', methods=['GET'])
@AuthController.token_required
def get_questions(current_user):
    return CampaignsQuestionController.get_all_questions()

@campaigns_question_bp.route('/api/quiz', methods=['POST'])
@AuthController.token_required
def create_question(current_user):
    return CampaignsQuestionController.create_question()

@campaigns_question_bp.route('/api/quiz/<int:question_id>', methods=['GET'])
@AuthController.token_required
def get_question(current_user, question_id):
    return CampaignsQuestionController.get_question(question_id)

@campaigns_question_bp.route('/api/quiz/<int:question_id>', methods=['PUT'])
@AuthController.token_required
def update_question(current_user, question_id):
    return CampaignsQuestionController.update_question(question_id)

@campaigns_question_bp.route('/api/quiz/<int:question_id>', methods=['DELETE'])
@AuthController.token_required
def delete_question(current_user, question_id):
    return CampaignsQuestionController.delete_question(question_id)

@campaigns_question_bp.route('/api/quiz/enabled', methods=['GET'])
@AuthController.token_required
def get_active_questions(current_user):
    return CampaignsQuestionController.get_active_questions()

@campaigns_question_bp.route('/api/quiz/disabled', methods=['GET'])
@AuthController.token_required
def get_inactive_questions(current_user):
    return CampaignsQuestionController.get_inactive_questions() 