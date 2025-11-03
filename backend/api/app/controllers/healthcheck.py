from flask import Blueprint, jsonify

healthcheck_bp = Blueprint('healthcheck', __name__)


@healthcheck_bp.route('', methods=['GET'])
def health_check():
    return jsonify({'status': 200, 'ok': True})
