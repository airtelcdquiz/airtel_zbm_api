from flask import Blueprint
from controllers.statistics_controller import StatisticsController
from controllers.auth_controller import AuthController

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/api/statistics/user-points', methods=['GET'])
@AuthController.token_required
def get_user_points(current_user):
    return StatisticsController.get_user_points() 
