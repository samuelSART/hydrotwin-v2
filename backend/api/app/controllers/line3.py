
import os
from datetime import datetime
from flask import Blueprint, request, jsonify

from app.models import line3


line3_bp = Blueprint('line3', __name__)


@line3_bp.route('/evapotranspiration/add-product', methods=['GET'])
def add_evapotranspiration_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] + "T03:00:00"
            date = datetime.strptime(date, "%Y%m%dT%H:%M:%S")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date  + "T03:00:00", "%Y%m%dT%H:%M:%S")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    
    try:
        result = line3.add_evapotranspiration_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line3_bp.route('/evapotranspiration-monthly/add-product', methods=['GET'])
def add_evapotranspiration_monthly_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1]
            date = datetime.strptime(date, "%Y%m")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    
    try:
        result = line3.add_evapotranspiration_monthly_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line3_bp.route('/waterdemand/add-product', methods=['GET'])
def add_waterdemand_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] + "T03:00:00"
            date = datetime.strptime(date, "%Y%m%dT%H:%M:%S")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date  + "T03:00:00", "%Y%m%dT%H:%M:%S")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line3.add_waterdemand_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line3_bp.route('/waterdemand-monthly/add-product', methods=['GET'])
def add_waterdemand_monthly_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1]
            date = datetime.strptime(date, "%Y%m")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line3.add_waterdemand_monthly_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line3_bp.route('/biomass/add-product', methods=['GET'])
def add_biomass_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1]
            date = datetime.strptime(date, "%Y%m")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line3.add_biomass_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line3_bp.route('/irrigation/add-product', methods=['GET'])
def add_irrigation_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] 
            date = datetime.strptime(date, "%Y%m")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line3.add_irrigation_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line3_bp.route('/crop-type/add-product', methods=['GET'])
def add_crop_type_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] 
            date = datetime.strptime(date, "%Y%m")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date, "%Y%m")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line3.add_crop_type_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500




@line3_bp.route('/irrigation-advice/add-product', methods=['GET'])
def add_irrigation_advice_data():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    file = request.args.get('file') if data is not None and 'file' in data else None
    
    if file is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter file, you have to specify path to GeoTiff file.', 'ok': False}), 400
    
    if date is None:
        try:
            filename = os.path.basename(file)
            date = filename.split("_")[1] + "T03:00:00"
            date = datetime.strptime(date, "%Y%m%dT%H:%M:%S")
        except Exception as e:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Can not infer date from filename, expected format <text>_%YEAR%MONTH%DAY_<...>', 'ok': False}), 400
    else:
        try:
            date = datetime.strptime(date  + "T03:00:00", "%Y%m%dT%H:%M:%S")
        except:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Wrong date, expected format %YEAR%MONTH%DAY', 'ok': False}), 400
    try:
        result = line3.add_irrigation_advice_product(file, date)
        if result:
            return jsonify({'status': 200, 'data': "Raster product correctly inserted", 'ok': True})
        return jsonify({'status': 500, 'title': 'Error', 'detail': "Raster images not found", 'ok': False}), 500
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
