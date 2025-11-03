from flask import Blueprint, jsonify, request
from app.models.drought_indices import DroughtIndices, drought_indices_schema

drought_indices_bp = Blueprint('drought-indices', __name__)


@drought_indices_bp.route('/get-drought-indices', methods=['POST'])
def get_drought_indices():
    data = request.get_json()
    date = data.get('date') if data and 'date' in data and (
        isinstance(data['date'], list) and len(data['date']) > 0) else None

    type = data.get('type') if data and 'type' in data else None
    range = data.get('range') if data and 'range' in data else None
    latest = data.get('latest') if data and 'latest' in data else True

    if type is None:
        return jsonify({'status': 400, 'title': 'Error',
                        'detail': 'Missing type.', 'ok': False}), 400
    try:
        if type == 'all':
            values = drought_indices_schema.dump(
                DroughtIndices.get_all_values())
            return jsonify({'status': 200, 'data': values, 'ok': True})

        if type == 'day':
            values = drought_indices_schema.dump(
                DroughtIndices.get_day_values(date,latest))
            return jsonify({'status': 200, 'data': values, 'ok': True})

        if type == 'custom':
            if range is None:
                return jsonify({'status': 400, 'title': 'Error',
                                'detail': 'Missing range.', 'ok': False}), 400
            values = drought_indices_schema.dump(
                DroughtIndices.get_range_values(range['start'], range['end'], latest))

            return jsonify({'status': 200, 'data': values, 'ok': True})

        return jsonify({'status': 400, 'title': 'Error',
                        'detail': 'Missing type.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
