import os
import glob
from flask import Blueprint, request, jsonify, current_app

from app.utils import geoutils


ows_bp = Blueprint('ows', __name__)


OWS_URL = current_app.config['OWS_URL']
GEODATA_ROOT_FOLDER = current_app.config['DATA_FOLDER']


@ows_bp.route('/init-odc/', methods=['GET'])
def init_odc():
    try:
        geoutils.init_odc()
        geoutils.add_metadata(GEODATA_ROOT_FOLDER+"/metadata/eo3.yaml")
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ows_bp.route('/add-product/', methods=['PUT'])
def add_product():
    data = request.get_json()
    product = data.get('product') if data and 'product' in data and (isinstance(data['product'], list) and len(data['product']) > 0) else None
    
    if product is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing body field: product, you have to specify the product schema.', 'ok': False}), 400
    
    try:
        geoutils.add_product_doc(product)
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ows_bp.route('/add-all-products/', methods=['GET'])
def add_metadata():
    try:
        failed = []
        for file in glob.glob(f'{GEODATA_ROOT_FOLDER}/metadata/product/*.yaml'):
            if not geoutils.add_product(file):
                failed.append(file)
        
        if len(failed) > 0:
            return jsonify({'status': 199, 'title': 'Warning', 'detail': {'The following products could not be added:': failed}, 'ok': False})
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ows_bp.route('/update-all-products/', methods=['GET'])
def update_metadata():
    try:
        failed = []
        for file in glob.glob(f'{GEODATA_ROOT_FOLDER}/metadata/product/*.yaml'):
            if not geoutils.update_product(file):
                failed.append(file)
        
        if len(failed) > 0:
            return jsonify({'status': 199, 'title': 'Warning', 'detail': {'The following products could not be updated:': failed}, 'ok': False})
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ows_bp.route('/add-all-datasets/', methods=['GET'])
def add_dataset():
    try:
        dataset_groups = {}
        failed = []
        
        for dataset_group in os.listdir(f'{GEODATA_ROOT_FOLDER}/metadata/dataset/'):
            dataset_groups[dataset_group] = glob.glob(f'{GEODATA_ROOT_FOLDER}/metadata/dataset/{dataset_group}/**/*.yaml', recursive=True)
        
        for dataset_group in dataset_groups:
            for dataset in dataset_groups[dataset_group]:
                if not geoutils.add_dataset(metadata_file=dataset, product=dataset_group):
                    failed.append(dataset)
        
        if len(failed) > 0:
            return jsonify({'status': 199, 'title': 'Warning', 'detail': {'The following datasets could not be added:': failed}, 'ok': False})
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ows_bp.route('/update-ows/', methods=['GET'])
def update_ows():
    import requests
    try:
        requests.get(f"{OWS_URL}/update")
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500

