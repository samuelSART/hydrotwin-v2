
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify

from app.models import line2


line2_bp = Blueprint('line2', __name__)


@line2_bp.route('/exchange/add-product', methods=['GET'])
def add_exchange_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    date = request.args.get('date') if data is not None and 'date' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] 
            date = datetime.strptime(date, "%Y%m%d")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m%d")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line2.add_exchange_product(file,date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line2_bp.route('/infiltration/add-product', methods=['GET'])
def add_infiltration_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    date = request.args.get('date') if data is not None and 'date' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] 
            date = datetime.strptime(date, "%Y%m%d")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m%d")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line2.add_infiltration_product(file,date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line2_bp.route('/recharge/add-product', methods=['GET'])
def add_recharge_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    date = request.args.get('date') if data is not None and 'date' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] 
            date = datetime.strptime(date, "%Y%m%d")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m%d")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line2.add_recharge_product(file,date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line2_bp.route('/water-content/add-product', methods=['GET'])
def add_water_content_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    date = request.args.get('date') if data is not None and 'date' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] 
            date = datetime.strptime(date, "%Y%m%d")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m%d")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line2.add_water_content_product(file,date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line2_bp.route('/simulation/add-values', methods=['GET'])
def add_simulation_products():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    simulation_range = request.args.get('simulation_range') if data is not None and 'simulation_range' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the DSF0 M11 or SZ file.', 'ok': False}), 400
    
    try:
        range = simulation_range if simulation_range else file.split('/')[2] # SIMUL_S or SIMUL_M
    except Exception as e:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer simulation range from file path', 'ok': False}), 400
    
    try:
        status, result = line2.add_dfs0_products(file, range)
        if status:
            return jsonify({'status': 200, 'data': "Simulation values correctly inserted", 'ok': True})
        else:
            return jsonify({'status': 500, 'title': 'Error', 'detail': str(result), 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line2_bp.route('/simulation/get-values', methods=['POST'])
def get_simulation_products():
    data = request.get_json()
    
    variables = data.get('variables') if data and 'variables' in data and (
        isinstance(data['variables'], list) and len(data['variables']) > 0) else None
    start_date = data.get('start_date') if data and 'start_date' in data else None
    end_date = data.get('end_date') if data and 'end_date' in data else None
    simulation_range = data.get('simulation_range') if data and 'simulation_range' in data else 0
    aggregation = data.get('aggregation') if data and 'aggregation' in data else None
    window = data.get('window') if data and 'window' in data else None

    if variables != None and start_date != None and end_date != None:
        status, result = line2.get_dfs0_products(variables, start_date, end_date, simulation_range, aggregation, window)
        if status:
            return jsonify({'status': 200, 'data': json.loads(result), 'ok': True})
        else:
            return jsonify({'status': 500, 'title': 'Error', 'detail': str(result), 'ok': False}), 500
    else:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query paramenters, you have to specify a start date, end date and a list of variables.', 'ok': False}), 400

