from flask import Blueprint, request, jsonify

from ..models.dam import DamModel, dams_schema

dam_bp = Blueprint('dam', __name__)


@dam_bp.route('/get-dams-variables', methods=['GET'])
def get_dams_variables():
    try:
        dams_variables = dams_schema.dump(DamModel.get_dams_variables())
        return jsonify({'status': 200, 'data': dams_variables, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@dam_bp.route('/get-dam-variables', methods=['GET'])
def get_dam_variables():
    dam = request.args.get('dam')

    try:
        if dam != None:
            dam_variables = dams_schema.dump(DamModel.get_dam_variables(dam))
            return jsonify({'status': 200, 'data': dam_variables, 'ok': True})
        else:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query paramenter, you have to specify dam code.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@dam_bp.route('/get-dams-variable-typology', methods=['GET'])
def get_dams_variable_typology():
    typology = request.args.get('typology')

    try:
        if typology != None:
            dams_variable_typology = dams_schema.dump(
                DamModel.get_dams_variable_typology(typology))
            return jsonify({'status': 200, 'data': dams_variable_typology, 'ok': True})
        else:
            return jsonify({'status': 400, 'title': 'Bad Request', 'detail': 'Missing query paramenter, you have to specify typology.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@dam_bp.route('/get-dam-by-variable', methods=['GET'])
def get_dam_by_variable():
    variable = request.args.get('variable')

    try:
        if variable != None:
            dam = dams_schema.dump(
                DamModel.get_dam_by_variable(variable))
            return jsonify({'status': 200, 'data': dam, 'ok': True})
        else:
            return jsonify({'status': 400, 'title': 'Bad Request', 'detail': 'Missing query paramenter, you have to specify dam.', 'ok': False}), 400
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
