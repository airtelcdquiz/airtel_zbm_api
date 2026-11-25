"""Journal des SMS (accusés de réception de l'opérateur), réservé à l'administrateur global.

Les données viennent du service SMS (GET /logs, réseau interne) : on relaie seulement.
"""
import os
import re

import requests
from flask import Blueprint, jsonify, request

from controllers.auth_controller import AuthController
from utils.access import superuser_required

sms_log_bp = Blueprint('sms_logs', __name__)

_SEND_URL = os.getenv('SMS_API_URL', 'http://js-sms-worker-api:3000/send-sms')
SMS_LOGS_URL = os.getenv('SMS_LOGS_URL') or re.sub(r'/send-sms/?$', '', _SEND_URL).rstrip('/') + '/logs'

_STATUSES = {'submitted', 'delivered', 'rejected', 'undelivered', 'failed', 'failures'}
_KINDS = {'otp', 'message', 'bulk'}


def _phone(raw):
    """0997…, 997…, +243997… → 243997… (recherche partielle acceptée)."""
    digits = re.sub(r'\D', '', raw or '')
    if digits.startswith('0'):
        digits = '243' + digits[1:]
    elif len(digits) == 9:
        digits = '243' + digits
    return digits


@sms_log_bp.route('/api/sms-logs', methods=['GET'])
@AuthController.token_required
@superuser_required
def sms_logs(current_user):
    params = {}
    phone = _phone(request.args.get('phone'))
    if phone:
        params['phone'] = phone
    status = request.args.get('status')
    if status in _STATUSES:
        params['status'] = status
    kind = request.args.get('kind')
    if kind in _KINDS:
        params['kind'] = kind
    try:
        params['limit'] = max(1, min(int(request.args.get('limit', 50)), 200))
    except ValueError:
        params['limit'] = 50
    before = request.args.get('before')
    if before and before.isdigit():
        params['before'] = before
    try:
        r = requests.get(SMS_LOGS_URL, params=params, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except requests.RequestException:
        return jsonify({'error': 'Le journal SMS est momentanément indisponible'}), 502
