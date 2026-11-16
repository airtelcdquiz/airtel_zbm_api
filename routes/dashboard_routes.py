from flask import Blueprint

from controllers.auth_controller import AuthController
from controllers.dashboard_controller import DashboardController

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard/overview', methods=['GET'])
@AuthController.token_required
def overview(current_user):
    return DashboardController.overview(current_user)
