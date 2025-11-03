from flask import Blueprint, request, jsonify, current_app
import json

from app import influx_client
from app.models.control_point import ControlPointModel, control_points_schema
from app.models.measurement_point import MeasurementPointModel, measurement_points_schema
from app.models.variable import VariableModel, variables_schema

saih_bp = Blueprint('saih', __name__)
BUCKET = current_app.config['SAIH_BUCKET']


@saih_bp.route('/get-variable-values', methods=['POST'])
def get_values():
    data = request.get_json()

    try:
        variables = data.get('variables') if data and 'variables' in data and (
            isinstance(data['variables'], list) and len(data['variables']) > 0) else None
        start_date = data.get(
            'start_date') if data and 'start_date' in data else None
        end_date = data.get(
            'end_date') if data and 'end_date' in data else None
        aggregation = data.get(
            'aggregation') if data and 'aggregation' in data else None
        window = data.get('window') if data and 'window' in data else None

        if variables != None and start_date != None and end_date != None:
            query_client = influx_client.query_api()

            query_variables = ''
            for index, variable_code in enumerate(variables):
                query_variables += 'r["variableCode"] == "' + \
                    variable_code + '"'
                if (index < len(variables) - 1):
                    query_variables += ' or '

            query = f'from(bucket: "{BUCKET}") \
                |> range(start: time(v: "{start_date}"), stop: time(v: "{end_date}")) \
                |> filter(fn: (r) => r["_measurement"] == "saih") \
                |> filter(fn: (r) => r["_field"] == "value") \
                |> filter(fn: (r) => ' + query_variables + ')'

            if aggregation != None and window != None:
                query = f'{query} |> aggregateWindow(every: {window}, fn: {aggregation}, createEmpty: false)'

            query = f'{query} |> keep(columns: ["_time", "_value", "variableCode"])'

            df = query_client.query_data_frame(query)

            if not df.empty:
                df.drop(columns=['result', 'table'], inplace=True)

            return jsonify({'status': 200, 'data': json.loads(df.to_json(orient='records')), 'ok': True})
        else:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query paramenters, you have to specify a start date, end date and variables.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/get-variable-last-values', methods=['POST'])
def get_last_values():
    data = request.get_json()

    try:
        variables = data.get('variables') if data and 'variables' in data and (
            isinstance(data['variables'], list) and len(data['variables']) > 0) else None

        if variables != None:
            query_client = influx_client.query_api()

            query_variables = ''
            for index, variable_code in enumerate(variables):
                query_variables += 'r["variableCode"] == "' + \
                    variable_code + '"'
                if (index < len(variables) - 1):
                    query_variables += ' or '

            query = f'from(bucket: "{BUCKET}") \
                |> range(start: -60d) \
                |> filter(fn: (r) => r["_measurement"] == "saih") \
                |> filter(fn: (r) => r["_field"] == "value") \
                |> filter(fn: (r) => ' + query_variables + ') \
                |> keep(columns: ["_time", "_value", "variableCode"]) \
                |> sort(columns: ["_time"], desc: true) \
                |> first()'

            df = query_client.query_data_frame(query)

            if not df.empty:
                df.drop(columns=['result', 'table'], inplace=True)

            return jsonify({'status': 200, 'data': json.loads(df.to_json(orient='records')), 'ok': True})
        else:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query paramenters, you have to specify a list of variables.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/get-last-timestamp', methods=['GET'])
def get_last_timestamp():
    try:
        data = request.get_json()
        _bucket = data.get(
            'bucket') if 'bucket' in data and data['bucket'] != "" else BUCKET
        query_client = influx_client.query_api()

        query = f'from(bucket: "{_bucket}") \
            |> range(start: -60d) \
            |> filter(fn: (r) => r["_measurement"] == "saih") \
            |> keep(columns: ["_time"]) \
            |> sort(columns: ["_time"], desc: true) \
            |> first(column: "_time")'

        df = query_client.query_data_frame(query)
        last_timestamp = df.at[0, '_time'].strftime('%Y-%m-%dT%H:%M:%S%z')

        return jsonify({'status': 200, 'data': last_timestamp, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/get-control-points', methods=['POST'])
def get_control_points():
    data = request.get_json()
    control_points = data.get('control_points') if data and 'control_points' in data and (
        isinstance(data['control_points'], list) and len(data['control_points']) > 0) else None

    try:
        values = control_points_schema.dump(
            ControlPointModel.get_values(control_points))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/post-control-points', methods=['PUT'])
def post_control_points():
    data = request.get_json()
    control_points = data.get('control_points') if data and 'control_points' in data and (
        isinstance(data['control_points'], list) and len(data['control_points']) > 0) else None
    try:
        ControlPointModel.write_values(control_points)
        return jsonify({'status': 200, 'data': f'{len(control_points)} control points inserted/updated', 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/get-measurement-points', methods=['POST'])
def get_measurement_points():
    data = request.get_json()

    measurement_points = data.get('measurement_points') if data and 'measurement_points' in data and (
        isinstance(data['measurement_points'], list) and len(data['measurement_points']) > 0) else None
    typology = data.get('typology') if data and 'typology' in data and (
        isinstance(data['typology'], list) and len(data['typology']) > 0) else None

    try:
        values = measurement_points_schema.dump(
            MeasurementPointModel.get_values(measurement_points, typology))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/post-measurement-points', methods=['PUT'])
def post_measurement_points():
    data = request.get_json()
    measurement_points = data.get('measurement_points') if data and 'measurement_points' in data and (
        isinstance(data['measurement_points'], list) and len(data['measurement_points']) > 0) else None
    try:
        MeasurementPointModel.write_values(measurement_points)
        return jsonify({'status': 200, 'data': f'{len(measurement_points)} measurement points inserted/updated', 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/get-variables', methods=['POST'])
def get_variables():
    data = request.get_json()
    variables = data.get('variables') if data and 'variables' in data and (
        isinstance(data['variables'], list) and len(data['variables']) > 0) else None
    measurement_points = data.get('measurement_points') if data and 'measurement_points' in data and (
        isinstance(data['measurement_points'], list) and len(data['measurement_points']) > 0) else None
    typology = data.get('typology') if data and 'typology' in data and (
        isinstance(data['typology'], list) and len(data['typology']) > 0) else None

    try:
        values = variables_schema.dump(VariableModel.get_values(
            variables, measurement_points, typology))
        return jsonify({'status': 200, 'data': values, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/post-variables', methods=['PUT'])
def post_variables():
    data = request.get_json()
    variables = data.get('variables') if data and 'variables' in data and (
        isinstance(data['variables'], list) and len(data['variables']) > 0) else None
    try:
        VariableModel.write_values(variables)
        return jsonify({'status': 200, 'data': f'{len(variables)} variables inserted/updated', 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@saih_bp.route('/get-piezometers', methods=['GET'])
def get_piezometers():
    try:
        data = MeasurementPointModel.get_piezometers()
        return jsonify({'status': 200, 'data': measurement_points_schema.dump(data), 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
