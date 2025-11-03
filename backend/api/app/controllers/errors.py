from flask import Blueprint, request, jsonify
from werkzeug.exceptions import HTTPException

errors_bp = Blueprint('errors', __name__)


@errors_bp.app_errorhandler(HTTPException)
def generic_handler(e):
    return jsonify({'status': e.code, 'detail': e.description, 'title': e.name, 'ok': False}), e.code
