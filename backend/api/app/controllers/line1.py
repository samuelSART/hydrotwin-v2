from flask import Blueprint, request, jsonify

from app.models import line1


line1_bp = Blueprint('line1', __name__)


@line1_bp.route('/wrf/add-product', methods=['GET'])
def add_wrf_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    try:
        result = line1.add_wrf_product(file)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line1_bp.route('/wrf-daily/add-product', methods=['GET'])
def add_wrf_daily_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    try:
        result = line1.add_wrf_daily_product(file)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line1_bp.route('/wrf-monthly/add-product', methods=['GET'])
def add_wrf_monthly_product():
    data = request.args
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter. file, you have to specify the path of the NetCDF product.', 'ok': False}), 400
    
    try:
        result = line1.add_wrf_monthly_product(file)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500

