import os
import argparse
import dotenv
import logging
import requests
import json
import pandas as pd
from datetime import datetime, timezone
from io import StringIO, TextIOWrapper
from retry import retry

import ingestor
from sftp import sftp


APPNAME = os.path.basename(__file__).split('.')[0].upper()
DOTENV_FILE = os.getenv('DOTENV_FILE', '.env')
dotenv.load_dotenv(DOTENV_FILE)
DATA_ORIGIN = DATA_PATH = None
DEBUG = os.environ.get('DEBUG', default='False').upper() in ['TRUE', 'YES', '1']
FTP_HOST = os.getenv('FTP_HOST')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
API_URL = os.getenv('API_URL')

logging.basicConfig(
    format=f'[{APPNAME.replace("_", " ")}]'+' %(asctime)s |%(levelname)s| {%(module)s->%(funcName)s}: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z', level=(logging.DEBUG if DEBUG else logging.INFO))


def read_file(filename: str) -> list:
    if DATA_ORIGIN == 'ftp':
        data = ftp.get_file(filename)
        data = TextIOWrapper(data, encoding='utf-8').readlines()
    else:
        data = open(filename).readlines()
    
    return data


def parse_data(data: list, start_boundary: str, end_boundary: str) -> pd.DataFrame:
    idx = _start = _end = 0
    for line in data:
        if start_boundary in line:
            _start = idx + 2
        elif end_boundary in line:
            _end = idx - 3
            break
        idx += 1
    
    data = data[_start:_end]
    io_data = StringIO()
    for line in data: io_data.write(line)
    io_data.seek(0)
    df = pd.read_fwf(io_data, skiprows=[1])
    
    return df


@retry(tries=3, delay=10, backoff=1.5, logger=None)
def write_data(data: dict, endpoint: str):
    logging.info(f'Writing data to {endpoint}:')
    try:
        res = json.loads(requests.put(url=f'{API_URL}/saih{endpoint}', json=data).text)
        if res['status'] == 200:
            logging.info(f'[{res["status"]}] {res["data"]}')
        else:
            logging.error(f'[{res["status"]}] The following error occurred trying to write data into DB:\n{res["detail"]}')
            raise requests.exceptions.HTTPError
    except Exception as e:
        logging.error(f'The following error occurred trying to write data into DB: {e}')
        raise e


def main():
    logging.info('### STARTING SAIH ELEMENTS PARSING ###')
    if DATA_ORIGIN == 'ftp':
        global ftp
        global DATA_PATH
        ftp = sftp(host=FTP_HOST, user=FTP_USER, password=FTP_PASS)
        if DATA_PATH.endswith((".rpt", ".RPT")):
            files = [DATA_PATH]
        else:
            files = ftp.list_files(path=DATA_PATH)
            files = [DATA_PATH+file for file in files if file.endswith((".rpt", ".RPT"))]
    else:
        if os.path.isdir(DATA_PATH):
            files = [DATA_PATH+file for file in os.listdir(DATA_PATH) if file.endswith((".rpt", ".RPT"))]
        elif os.path.isfile(DATA_PATH):
            files = [DATA_PATH]
            DATA_PATH = os.path.dirname(DATA_PATH) + '/'
    files.sort()
    
    latest_file = ''
    last_file_date = datetime.fromtimestamp(timestamp=0, tz=timezone.utc)
    for file in files:
        file_date = datetime.strptime(file[len(DATA_PATH)+14:-4], "%Y%m%d").astimezone(tz=timezone.utc)
        if file_date > last_file_date:
            last_file_date = file_date
            latest_file = file
    
    logging.debug(f'Reading data from file {latest_file[len(DATA_PATH):]}...')
    data = read_file(latest_file)
    
    # Get control points and write to DB:
    control_points_rel = parse_data(data,
                                    'Relación de Puntos de Control  CDTI',
                                    'Relación de Puntos de Medición CDTI')
    control_points_rel.rename(columns={'CodPuntoControl': 'code',
                                       'Descripcion': 'denomination',
                                       'Municipio': 'municipality',
                                       'Provincia': 'province',
                                       'CodTipologiaPuntoControl': 'typology',
                                       'DescripcionTipologiaPuntoControl': 'description',
                                       'X_ETRS89': 'x', 'Y_ETRS89': 'y'}, inplace=True)
    write_data({"control_points": control_points_rel.to_dict(orient='records')}, '/post-control-points')
    
    # Get measurement points and write to DB:
    meas_points_rel = parse_data(data,
                                 'Relación de Puntos de Medición CDTI',
                                 'Relación de Variables asociadas a Puntos de Medición CDTI')
    meas_points_rel.rename(columns={'CodPuntoMedicion': 'code',
                                    'CodPuntoControl': 'control_point',
                                    'Descripcion': 'denomination',
                                    'DescripcionTipologiaPuntoMedicion': 'description',
                                    'CodTipologiaPuntoMedicion': 'typology',
                                    'X_ETRS89': 'x', 'Y_ETRS89': 'y',}, inplace=True)
    write_data({"measurement_points": meas_points_rel.to_dict(orient='records')}, '/post-measurement-points')
    
    # Get variables and write to DB:
    meas_var_rel = parse_data(data,
                              'Relación de Variables asociadas a Puntos de Medición CDTI',
                              'Relación de Variables Hidráulicas CDTI')
    meas_var_rel.rename(columns={'CodVariableHidrologica': 'code',
                                'CodPuntoMedicion': 'measurement_point',
                                'CodTipologiaVariableHidrologica': 'typology',
                                'DenominacionTipologiaVariable': 'description'}, inplace=True)
    write_data({"variables": meas_var_rel.to_dict(orient='records')}, '/post-variables')
    
    # hidro_vars_rel = parse_data(data,
    #                             'Relación de Variables Hidráulicas CDTI',
    #                             'Completion time')
    
    # Call reingestion process to load new variables that were previously not processed:
    ingestor.reingest()
    
    # If using FTP, close connection on finish
    try:
        if DATA_ORIGIN == 'ftp': ftp.disconnect()
    except:
        pass
    
    logging.info('### SAIH ELEMENTS PARSING FINISHED ###')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--origin', choices=['ftp', 'file'], default='ftp',
                        help='Origin of rpt files (default: %(default)s)')
    parser.add_argument('-p', '--path', default='./', help='Path of rpt files (default: %(default)s)')
    args = parser.parse_args()
    DATA_ORIGIN = args.origin
    DATA_PATH = ingestor.validate_data_path(data_path=args.path, data_origin=DATA_ORIGIN, valid_ext='.rpt')
    
    main()

