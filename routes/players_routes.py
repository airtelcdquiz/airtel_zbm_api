from flask import Blueprint
from controllers.players_controller import PlayersController
from controllers.auth_controller import AuthController
from utils.access import superuser_required

players_bp = Blueprint('players', __name__)


@players_bp.route('/api/players', methods=['GET'])
@AuthController.token_required
def list_players(current_user):
    return PlayersController.list_players(current_user)


@players_bp.route('/api/players/export', methods=['GET'])
@AuthController.token_required
def export_players(current_user):
    return PlayersController.export_players(current_user)


@players_bp.route('/api/players/labels', methods=['GET'])
@AuthController.token_required
def labels(current_user):
    return PlayersController.labels(current_user)


@players_bp.route('/api/admins', methods=['GET'])
@AuthController.token_required
@superuser_required
def list_admins(current_user):
    return PlayersController.list_admins(current_user)
