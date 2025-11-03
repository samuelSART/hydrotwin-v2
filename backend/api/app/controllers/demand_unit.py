from flask import Blueprint, request, jsonify

from ..models.demand_unit import DemandUnitModel, demand_units_schema
from ..utils.geoutils import inflates_geometry
demand_unit_bp = Blueprint('demand-unit', __name__)


@demand_unit_bp.route('/get-values', methods=['GET'])
def get_values():
    type = request.args.get('type')
    code = request.args.get('code')

    try:
        values = demand_units_schema.dump(
            DemandUnitModel.get_values(type, code))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@demand_unit_bp.route('/get-values-extended', methods=['GET'])
def get_values_extended():
    data = request.get_json()
    try:
        if data is None:
            values = demand_units_schema.dump(
                DemandUnitModel.get_values_extended(None))
        else:
            values = demand_units_schema.dump(
                DemandUnitModel.get_values_extended(data.get('code')))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@demand_unit_bp.route('/get-by-position', methods=['POST'])
def get_by_position():
    data = request.get_json()
    geometry = data.get(
        'geometry') if data is not None and 'geometry' in data else None
    distance = data.get(
        'distance') if data is not None and 'distance' in data else None

    if geometry is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing geometry or latitude and longitude.', 'ok': False}), 400

    try:
        if distance is None:
            distance = 100
        geometry = inflates_geometry(geometry, distance)
        values = demand_units_schema.dump(
            DemandUnitModel.get_by_position(geometry))

        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
