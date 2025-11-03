from os import getenv
from datetime import datetime
from flask import Blueprint, jsonify

version_bp = Blueprint('version', __name__)


@version_bp.route('', methods=['GET'])
def version():
    version = getenv('VERSION', default='nover')
    # return jsonify({'status': 200, 'ok': True, 'title': 'API version', 'version': version, 'copyright': f'HydroTwin (c) {datetime.now().year}'})
    return f'<h2>API version <i>{version}</i></h2><p>HydroTwin © {datetime.now().year}</p>'
