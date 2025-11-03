from flask import Blueprint, request, jsonify
from app.models.system_unit import SystemUnitModel, system_units_schema

system_unit_bp = Blueprint('system-unit', __name__)

@system_unit_bp.route('/get-values', methods=['GET'])
def get_values():
    data = request.get_json()

    try:
        if data is None:
            values = system_units_schema.dump(SystemUnitModel.get_values(None))
        else:
            values = system_units_schema.dump(SystemUnitModel.get_values(data.get('code')))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
    
