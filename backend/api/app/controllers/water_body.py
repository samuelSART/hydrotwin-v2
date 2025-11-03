from flask import Blueprint, request, jsonify
from app.models.water_body import WaterBodyModel, water_bodies_schema
from app.utils.geoutils import inflates_geometry
water_body_bp = Blueprint('-body', __name__)


@water_body_bp.route('/get-values', methods=['GET'])
def get_values():
    code = request.args.get('code')
    wb_type = request.args.get('type')

    try:
        values = water_bodies_schema.dump(
            WaterBodyModel.get_values(code, wb_type))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@water_body_bp.route('/get-by-position', methods=['POST'])
def get_by_position():
    data = request.get_json()
    geometry = data.get(
        'geometry') if data is not None and 'geometry' in data else None
    distance = data.get(
        'distance') if data is not None and 'distance' in data else None

    if geometry is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing geometry.', 'ok': False}), 400

    try:
        if distance is None:
            distance = 100
        geometry = inflates_geometry(geometry, distance)
        values = water_bodies_schema.dump(
            WaterBodyModel.get_by_position(geometry))

        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
