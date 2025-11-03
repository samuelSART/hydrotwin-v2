import os
import uuid
import mikeio
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS

from flask import current_app
from app import influx_client
from app.utils import geoutils


DATA_FOLDER = current_app.config['DATA_FOLDER']
BUCKET = current_app.config['SIMUL_BUCKET']
EXCHANGE_TEMPLATE = "metadata/template/exchange_template.yaml"
INFILTRATION_TEMPLATE = "metadata/template/infiltration_template.yaml"
RECHARGE_TEMPLATE = "metadata/template/recharge_template.yaml"
WATER_CONTENT_TEMPLATE = "metadata/template/water_content_template.yaml"
EXCHANGE_METADATA_PATH = Path(DATA_FOLDER, "metadata/dataset/exchange/")
INFILTRATION_METADATA_PATH = Path(DATA_FOLDER, "metadata/dataset/infiltration/")
RECHARGE_METADATA_PATH = Path(DATA_FOLDER, "metadata/dataset/recharge/")
WATER_CONTENT_METADATA_PATH = Path(DATA_FOLDER, "metadata/dataset/water_content/")


def add_exchange_product(file, date):
    template_file = Path(DATA_FOLDER, EXCHANGE_TEMPLATE)
    return add_product(file,date, template_file, "path", EXCHANGE_METADATA_PATH, "exchange")


def add_infiltration_product(file, date):
    template_file = Path(DATA_FOLDER, INFILTRATION_TEMPLATE)
    return add_product(file,date, template_file, "path", INFILTRATION_METADATA_PATH, "infiltration")


def add_recharge_product(file, date):
    template_file = Path(DATA_FOLDER, RECHARGE_TEMPLATE)
    return add_product(file,date, template_file, "path", RECHARGE_METADATA_PATH, "recharge")


def add_water_content_product(file, date):
    template_file = Path(DATA_FOLDER, WATER_CONTENT_TEMPLATE)
    return add_product(file,date, template_file, "path", WATER_CONTENT_METADATA_PATH, "water_content")


def add_product(file, date, template_file, band, metadata_folder, product ):
    file_path = Path(DATA_FOLDER, file)
    
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
        'datetime' : date_str,
        'polygon': polygon,
        'shape': shape,
        'transform': transform,
        "lat_min":lat_min,
        "lat_max":lat_max,
        "lon_min":lon_min,
        "lon_max": lon_max,
        band : file_path
    }
    
    with open(template_file, 'r') as f:
        template = f.read()
    filled_template = template.format(**values)
    

    metadata_file = os.path.join(metadata_folder, "L2_{}_metadata_{}.yaml".format(product,date.strftime("%Y%m%d")))
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
    
    geoutils.add_dataset(metadata_file,product)
    
    return True


def add_dfs0_products(file, interval):
    mk_file = mikeio.read(Path(DATA_FOLDER, file))
    df = mk_file.to_dataframe()
    
    # Rename columns
    for column in df.columns:
        try:
            varID = column.split('(')[1].split(')')[0]
            df.rename(columns={column: varID}, inplace=True)
        except:
            logging.warning(f'Unrenamed column @ \'{file}\': {column}')
    
    # Unpivot a DataFrame from wide to long format
    df = pd.melt(df, value_vars=df.columns, ignore_index=False)
    df.sort_index(inplace=True)
    
    # Write to Influx
    try:
        write_client = influx_client.write_api(write_options=SYNCHRONOUS)
        write_client.write(BUCKET, record=df, data_frame_measurement_name=interval,
                            data_frame_tag_columns=['variable'])
        write_client.close()
        return True, 'OK'
    except Exception as e:
        return False, f'Error writing \'{file}\' data for measurement \'{interval}\' in bucket \'{BUCKET}\': {str(e)}'


def get_dfs0_products(variables = None, start_date = None, end_date = None, interval = 0, aggregation = None, window = None):
    try:
        query_client = influx_client.query_api()
        query_variables = ''
        
        for index, variable_code in enumerate(variables):
            query_variables += 'r["variable"] == "' + \
                variable_code + '"'
            if (index < len(variables) - 1):
                query_variables += ' or '
        
        measurement = 'SIMUL_S' if interval == 0 else 'SIMUL_M'
        
        query = f'from(bucket: "{BUCKET}") \
            |> range(start: time(v: "{start_date}"), stop: time(v: "{end_date}")) \
            |> filter(fn: (r) => r["_measurement"] == "{measurement}") \
            |> filter(fn: (r) => r["_field"] == "value") \
            |> filter(fn: (r) => ' + query_variables + ')'
        
        if aggregation != None and window != None:
            query = f'{query} |> aggregateWindow(every: {window}, fn: {aggregation}, createEmpty: false)'
        
        query = f'{query} |> keep(columns: ["_time", "_value", "variable"])'
        df = query_client.query_data_frame(query)
        
        if not df.empty:
            df.drop(columns=['result', 'table'], inplace=True)
        
        return True, df.to_json(orient='records')
    except Exception as e:
        return False, f'Error querying \'{BUCKET}\' bucket: {str(e)}'

