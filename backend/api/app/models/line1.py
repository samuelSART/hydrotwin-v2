import os
import uuid
import logging
from datetime import datetime

from flask import current_app
from app.utils import geoutils


DATA_FOLDER = current_app.config['DATA_FOLDER']
WRF_TEMPLATE = "/metadata/template/wrf_template.yaml"
WRF_DAILY_TEMPLATE = "/metadata/template/wrf_daily_template.yaml"
WRF_MONTHLY_TEMPLATE = "/metadata/template/wrf_monthly_template.yaml"
WRF_METADATA_ROOT = "/metadata/dataset/wrf/"
WRF_DAILY_METADATA_ROOT = "/metadata/dataset/wrf_daily/"
WRF_MONTHLY_METADATA_ROOT = "/metadata/dataset/wrf_monthly/"
WRF_METADATA_PATH = DATA_FOLDER + WRF_METADATA_ROOT
WRF_DAILY_METADATA_PATH = DATA_FOLDER + WRF_DAILY_METADATA_ROOT
WRF_MONTHLY_METADATA_PATH = DATA_FOLDER + WRF_MONTHLY_METADATA_ROOT


def add_wrf_product(file):
    template_file = DATA_FOLDER + WRF_TEMPLATE
    
    file_path = DATA_FOLDER + file
    if not os.path.isfile(file_path):
        return False
    file_path = geoutils.netcdf_clean(file_path)
    creation_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
    polygon, shape, transform, date_list = geoutils.netcdf_get_properties(
        file_path)
    lat_list = list(list(zip(*polygon[0]))[1])
    lon_list = list(list(zip(*polygon[0]))[0])
    lat_min = min(lat_list)
    lat_max = max(lat_list)
    lon_min = min(lon_list)
    lon_max = max(lon_list)
    logging.debug("Dates found {}".format(len(date_list)))
    
    for e, date in enumerate(date_list):
        
        uid = uuid.uuid4()
        datetime_obj = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')
        datetime_str = datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        values = {
            'uid': uid,
            'creation_date': creation_date,
            'polygon': polygon,
            'shape': shape,
            'transform': transform,
            'datetime': datetime_str,
            "lat_min":lat_min,
            "lat_max":lat_max,
            "lon_min":lon_min,
            "lon_max": lon_max,
            'path': "file://"+file_path+"#part={}".format(str(e))
        }
        
        with open(template_file, 'r') as f:
            template = f.read()
        filled_template = template.format(**values)
        
        metadata_file = os.path.join(WRF_METADATA_PATH, "L1_wrf_metadata_{}.yaml".format(datetime_obj.strftime("%Y%m%d_%H")))
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
        geoutils.add_dataset(metadata_file,"wrf")
    
    return True


def add_wrf_daily_product(file):
    template_daily_file = DATA_FOLDER + WRF_DAILY_TEMPLATE
    file_path = DATA_FOLDER + file
    if not os.path.isfile(file_path):
        return False
    
    creation_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
    tif_files, dates = geoutils.netcdf_to_geotiff(file_path)
    polygon, shape, transform = geoutils.geotif_get_properties(tif_files[0])
    lat_list = list(list(zip(*polygon[0]))[1])
    lon_list = list(list(zip(*polygon[0]))[0])
    lat_min = min(lat_list)
    lat_max = max(lat_list)
    lon_min = min(lon_list)
    lon_max = max(lon_list)
    
    for e, tif_file in enumerate(tif_files):
        uid = uuid.uuid4()
        datetime_obj = datetime.strptime(str(dates[e]), '%Y-%m-%d')
        datetime_str = str(dates[e])
        values = {
            'uid': uid,
            'creation_date': creation_date,
            'polygon': polygon,
            'shape': shape,
            'transform': transform,
            'datetime': datetime_str,
            "lat_min":lat_min,
            "lat_max":lat_max,
            "lon_min":lon_min,
            "lon_max": lon_max,
            'path': tif_file
        }
        
        with open(template_daily_file, 'r') as f:
            template = f.read()
        filled_template = template.format(**values)

        metadata_file = os.path.join(WRF_DAILY_METADATA_PATH, "L1_wrf_daily_metadata_{}.yaml".format(datetime_obj.strftime("%Y%m%d")))
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
        geoutils.add_dataset(metadata_file,"wrf_daily")
    
    return True


def add_wrf_monthly_product(file):
    template_daily_file = DATA_FOLDER + WRF_MONTHLY_TEMPLATE
    file_path = DATA_FOLDER + file
    if not os.path.isfile(file_path):
        return False
    
    creation_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    tif_files, dates = geoutils.netcdf_to_geotiff(file_path)
    
    polygon, shape, transform = geoutils.geotif_get_properties(tif_files[0])
    lat_list = list(list(zip(*polygon[0]))[1])
    lon_list = list(list(zip(*polygon[0]))[0])
    lat_min = min(lat_list)
    lat_max = max(lat_list)
    lon_min = min(lon_list)
    lon_max = max(lon_list)
    
    for e, tif_file in enumerate(tif_files):
        uid = uuid.uuid4()
        datetime_obj = datetime.strptime(str(dates[e]), '%Y-%m-%d')
        datetime_str = str(dates[e])
        values = {
            'uid': uid,
            'creation_date': creation_date,
            'polygon': polygon,
            'shape': shape,
            'transform': transform,
            'datetime': datetime_str,
            "lat_min":lat_min,
            "lat_max":lat_max,
            "lon_min":lon_min,
            "lon_max": lon_max,
            'path': tif_file
        }
        
        with open(template_daily_file, 'r') as f:
            template = f.read()
        filled_template = template.format(**values)
        

        metadata_file = os.path.join(WRF_MONTHLY_METADATA_PATH, "L1_wrf_monthly_metadata_{}.yaml".format(datetime_obj.strftime("%Y%m%d")))
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
        geoutils.add_dataset(metadata_file,"wrf_monthly")
    
    return True

