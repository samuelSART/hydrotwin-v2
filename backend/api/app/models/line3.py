import os
import uuid
from datetime import datetime

from flask import current_app
from app.utils import geoutils


DATA_FOLDER = current_app.config['DATA_FOLDER']
EVAPOTRANSPIRATION_TEMPLATE = "/metadata/template/evapotranspiration_template.yaml"
EVAPOTRANSPIRATION_MONTHLY_TEMPLATE = "/metadata/template/evapotranspiration_monthly_template.yaml"
WATERDEMAND_TEMPLATE = "/metadata/template/waterdemand_template.yaml"
WATERDEMAND_MONTHLY_TEMPLATE = "/metadata/template/waterdemand_monthly_template.yaml"
BIOMASS_TEMPLATE = "/metadata/template/biomass_template.yaml"
IRRIGATION_TEMPLATE = "/metadata/template/irrigation_template.yaml"
IRRIGATION_ADVICE_TEMPLATE = "/metadata/template/irrigation_advice_template.yaml"
IRRIGATION_PROBABILITY_TEMPLATE = "/metadata/template/irrigation_probability_template.yaml"
CROP_TYPE_TEMPLATE = "/metadata/template/crop_type_template.yaml"
EVAPOTRANSPIRATION_METADATA_PATH = DATA_FOLDER + \
    "/metadata/dataset/evapotranspiration/"
EVAPOTRANSPIRATION_MONTHLY_METADATA_PATH = DATA_FOLDER + \
    "/metadata/dataset/evapotranspiration_monthly/"
WATERDEMAND_METADATA_PATH = DATA_FOLDER + "/metadata/dataset/waterdemand/"
WATERDEMAND_MONTHLY_METADATA_PATH = DATA_FOLDER + \
    "/metadata/dataset/waterdemand_monthly/"
BIOMASS_METADATA_PATH = DATA_FOLDER + "/metadata/dataset/biomass/"
IRRIGATION_METADATA_PATH = DATA_FOLDER + "/metadata/dataset/irrigation/"
IRRIGATION_PROBABILITY_METADATA_PATH = DATA_FOLDER + \
    "/metadata/dataset/irrigation_probability/"
CROP_TYPE_METADATA_PATH = DATA_FOLDER + "/metadata/dataset/crop_type/"
IRRIGATION_ADVICE_METADATA_PATH = DATA_FOLDER + "/metadata/dataset/irrigation_advice/"

def add_evapotranspiration_product(file, date):
    template_file = DATA_FOLDER + EVAPOTRANSPIRATION_TEMPLATE
    return add_product(file, date, template_file, "ET", EVAPOTRANSPIRATION_METADATA_PATH, "evapotranspiration")


def add_evapotranspiration_monthly_product(file, date):
    template_file = DATA_FOLDER + EVAPOTRANSPIRATION_MONTHLY_TEMPLATE
    return add_product(file, date, template_file, "ET", EVAPOTRANSPIRATION_MONTHLY_METADATA_PATH, "evapotranspiration_monthly")


def add_waterdemand_product(file, date):
    template_file = DATA_FOLDER + WATERDEMAND_TEMPLATE
    return add_product(file, date, template_file, "WD", WATERDEMAND_METADATA_PATH, "waterdemand")


def add_waterdemand_monthly_product(file, date):
    template_file = DATA_FOLDER + WATERDEMAND_MONTHLY_TEMPLATE
    return add_product(file, date, template_file, "WD", WATERDEMAND_MONTHLY_METADATA_PATH, "waterdemand_monthly")


def add_biomass_product(file, date):
    template_file = DATA_FOLDER + BIOMASS_TEMPLATE
    return add_product(file, date, template_file, "BM", BIOMASS_METADATA_PATH, "biomass")


def add_irrigation_product(file, date):
    template_file = DATA_FOLDER + IRRIGATION_TEMPLATE
    return add_product(file, date, template_file, "IR", IRRIGATION_METADATA_PATH, "irrigation")


def add_irrigation_probability_product(file, date):
    template_file = DATA_FOLDER + IRRIGATION_PROBABILITY_TEMPLATE
    return add_product(file, date, template_file, "IRp", IRRIGATION_PROBABILITY_METADATA_PATH, "irrigation_probability")

def add_irrigation_advice_product(file, date):
    template_file = DATA_FOLDER + IRRIGATION_ADVICE_TEMPLATE
    return add_product(file, date, template_file, "IR_AD", IRRIGATION_ADVICE_METADATA_PATH, "irrigation_advice")


def add_crop_type_product(file, date):
    template_file = DATA_FOLDER + CROP_TYPE_TEMPLATE
    return add_product(file, date, template_file, "CT", CROP_TYPE_METADATA_PATH, "crop_type")


def add_product(file, date, template_file, band, metadata_folder, product):
    file_path = DATA_FOLDER + file
    if not os.path.isfile(file_path):
        return False
    date_str = date.strftime("%Y-%m-%dT%H:%M:%SZ")
    creation_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
    polygon, shape, transform = geoutils.geotif_get_properties(file_path)
    uid = uuid.uuid4()
    lat_list = list(list(zip(*polygon[0]))[1])
    lon_list = list(list(zip(*polygon[0]))[0])
    lat_min = min(lat_list)
    lat_max = max(lat_list)
    lon_min = min(lon_list)
    lon_max = max(lon_list)
    values = {
        'uid': uid,
        'creation_date': creation_date,
        'datetime': date_str,
        'polygon': polygon,
        'shape': shape,
        'transform': transform,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lon_min": lon_min,
        "lon_max": lon_max,
        band: file_path
    }
    
    with open(template_file, 'r') as f:
        template = f.read()
    filled_template = template.format(**values)
    
    metadata_file = os.path.join(metadata_folder, "L3_{}_metadata_{}.yaml".format(product,date.strftime("%Y%m%d")))
    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
    
    if os.path.isfile(metadata_file):
        import yaml
        from yaml.loader import SafeLoader
        with open(metadata_file) as f:
            data = yaml.load(f, Loader=SafeLoader)
        old_uuid = data['id']
        geoutils.archive_dataset(old_uuid)
    with open(metadata_file, 'w') as f:
        f.write(filled_template)
    
    geoutils.add_dataset(metadata_file, product)
    
    return True

