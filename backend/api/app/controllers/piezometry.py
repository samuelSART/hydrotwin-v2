from flask import Blueprint, request, jsonify
from app.models.piezometry import PiezometryModel, piezometries_schema
from app.models.piezometry_value import PiezometerValue, piezometry_values_schema


piezometry_bp = Blueprint('piezometry', __name__)


@piezometry_bp.route('/get-piezometers', methods=['POST'])
def get_piezometers():
    data = request.get_json()
    objectid = data.get('objectid') if data and 'objectid' in data and (
        isinstance(data['objectid'], list) and len(data['objectid']) > 0) else None
    cod_chs = data.get('cod_chs') if data and 'cod_chs' in data and (
        isinstance(data['cod_chs'], list) and len(data['cod_chs']) > 0) else None

    try:
        piezometers = piezometries_schema.dump(
            PiezometryModel.get_piezometers(objectid, cod_chs))
        return jsonify({'status': 200, 'data': piezometers, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@piezometry_bp.route('/get-piezometers-values', methods=['POST'])
def get_piezometers_values():
    data = request.get_json()

    variables = data.get('variables') if data and 'variables' in data and (
        isinstance(data['variables'], list) and len(data['variables']) > 0) else None

    type = data.get('type') if data and 'type' in data else None
    range = data.get('range') if data and 'range' in data else None

    if variables is None or type is None:
        return jsonify({'status': 400, 'title': 'Error',
                        'detail': 'Missing variables or type.', 'ok': False}), 400

    try:
        if type == 'latest':
            values = piezometry_values_schema.dump(
                PiezometerValue.get_latest_value(variables))
            return jsonify({'status': 200, 'data': values, 'ok': True})

        if type == 'initial':
            init_values = piezometry_values_schema.dump(
                PiezometerValue.get_first_value(variables))

            latest_value = piezometry_values_schema.dump(
                PiezometerValue.get_latest_value(variables))

            sorted_values = sorted(
                init_values + latest_value, key=lambda d: d['variableCode'])
            return jsonify({'status': 200, 'data': sorted_values, 'ok': True})

        if type == 'custom':
            if range is None:
                return jsonify({'status': 400, 'title': 'Error',
                                'detail': 'Missing range.', 'ok': False}), 400
            values = piezometry_values_schema.dump(
                PiezometerValue.get_range_values(variables, range['start'], range['end']))

            return jsonify({'status': 200, 'data': values, 'ok': True})

        return jsonify({'status': 400, 'title': 'Error',
                        'detail': 'type not supported.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
