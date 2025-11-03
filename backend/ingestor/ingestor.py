import os
import pytz
import dotenv
import signal
import psutil
import logging
import argparse
import requests
import pandas as pd
from math import ceil
from retry import retry
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import WriteType

from sftp import sftp


APPNAME = os.path.basename(__file__).split('.')[0].upper().replace("_", " ")
DOTENV_FILE = os.getenv('DOTENV_FILE', '.env')
dotenv.load_dotenv(DOTENV_FILE)
PIDFILE = f"{os.path.basename(__file__).split('.')[0]}.pid"
DATA_ORIGIN = DATA_PATH = DATA_SINCE = DATA_TIMEZONE = None
DEBUG = os.environ.get('DEBUG', default='False').upper() in ['TRUE', 'YES', '1']
FTP_HOST = os.getenv('FTP_HOST')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
API_URL = os.getenv('API_URL')
BUCKET = os.getenv('SAIH_BUCKET', default='SAIH')
RAW_DATA_BUCKET = f'{BUCKET}_raw'
MEASUREMENT = os.getenv('INFLUXDB_V2_MEASUREMENT', default='saih')
BUCKET_LOOKBACK_DAYS = os.getenv('BUCKET_LOOKBACK_DAYS', default=30)
TIMEOUT = int(os.getenv('TIMEOUT', 30))
if not os.getenv('INFLUXDB_V2_TIMEOUT'):
    os.environ["INFLUXDB_V2_TIMEOUT"] = str(TIMEOUT) + '000'

logging.basicConfig(
    format=f'[{APPNAME}]'+' %(asctime)s |%(levelname)s| {%(module)s->%(funcName)s}: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z', level=(logging.DEBUG if DEBUG else logging.INFO))

influx_client = InfluxDBClient.from_env_properties()
last_meas_point = last_typology = None


def check_process(pidfile):
    if os.path.isfile(pidfile):
        with open(pidfile, 'r') as f:
            file_pid = int(f.readline().strip())
        return psutil.pid_exists(file_pid)
    return False


def validate_data_path(data_path: str, data_origin: str, valid_ext: str) -> str:
    if data_origin == 'ftp':
        global ftp
        ftp = sftp(host=FTP_HOST, user=FTP_USER, password=FTP_PASS)
        try:
            ftp.client.stat(path=data_path)
            return f'{data_path}/' if not data_path.endswith(('/', valid_ext, valid_ext.upper())) else data_path
        except (IOError, FileNotFoundError) as e:
            raise FileNotFoundError(f'{data_path} does not exist or is innacesible: {e}')
    
    if os.path.exists(data_path):
        if os.path.isdir(data_path):
            return f'{data_path}/' if not data_path.endswith('/') else data_path
        elif os.path.isfile(data_path):
            if data_path.endswith((valid_ext,valid_ext.upper())):
                return data_path
            else:
                logging.error(f'Please provide a valid {valid_ext} file as input.')
                parser.print_help()
                exit(1)
    else:
        raise FileNotFoundError(f'{data_path} does not exist or is innacesible!')


@retry(tries=3, delay=10, logger=None)
def get_raw_data(bucket: str, range: int = 60) -> pd.DataFrame:
    logging.info(f'Getting data since {range} days back from {bucket} bucket...')
    try:
        query_client = influx_client.query_api()
        query = f'from(bucket: "{bucket}") \
            |> range(start: -{range}d) \
            |> filter(fn: (r) => r["_measurement"] == "saih")'
        
        _df = query_client.query_data_frame(query)
        _df.drop(columns=['result', 'table', '_start', '_stop', '_field', '_measurement'], inplace=True)
        _df.rename(columns={'_value': 'value'}, inplace=True)
        return _df
    except Exception as e:
        raise Exception(f'An error occurred trying to access InfluxDB: {e}')


def read_data(filename: str) -> pd.DataFrame:
    if DATA_ORIGIN == 'ftp':
        _data = ftp.get_file(filename=filename)
    else:
        _data = filename
    
    logging.info(f'Reading data from file {filename[len(DATA_PATH):]}...')
    df = pd.DataFrame()
    # Example row: 30-03-2022 14:20;01A01A1;N;32,510;cm
    df = pd.read_csv(_data, delimiter=';', names=['date', 'measurementPointCode', 'typology', 'value', 'unit'],
                    parse_dates=[0], dayfirst=True, thousands='.', decimal=',', na_values='-', index_col=['date']).fillna(0)
    df.sort_index(inplace=True)
    df = df.tz_localize(DATA_TIMEZONE, ambiguous=False, nonexistent=pd.Timedelta('-1h'))
    return df


@retry(tries=3, delay=10, logger=None)
def write_data(data: pd.DataFrame, bucket: str, measurement: str, tags: dict):
    logging.debug(f'Writing data to bucket {bucket}...')
    if not influx_client.buckets_api().find_bucket_by_name(bucket):
        influx_client.buckets_api().create_bucket(bucket_name=bucket)
    
    try:
        write_client = influx_client.write_api(write_options=WriteOptions(
                        write_type=WriteType.batching, batch_size=500, flush_interval=1000))
        write_client.write(bucket, record=data, data_frame_measurement_name=measurement,
                            data_frame_tag_columns=tags)
        write_client.close()
    except Exception as e:
        raise Exception(f'Error writing data for measurement {measurement} in bucket {bucket}: {str(e)}')


@retry(tries=3, delay=10)
def delete_data(start_time, stop_time, measurement, measurement_point_code, typology, bucket):
    delete_api = influx_client.delete_api()
    logging.debug(f'Deleting {measurement_point_code}:{typology} @ {start_time} from bucket {bucket}.')
    delete_api.delete(start_time, stop_time,
        f'_measurement="{measurement}" AND measurementPointCode="{measurement_point_code}" AND typology="{typology}"',
        bucket=bucket)


@retry(delay=10, backoff=1.5, max_delay=TIMEOUT, logger=None)
def get_last_record_from_api(bucket: str):
    resp = requests.get(url=f'{API_URL}/saih/get-last-timestamp', json={"bucket": f"{bucket}"})
    if resp.status_code == 200:
        try:
            last_record_date = datetime.strptime(resp.json()['data'], '%Y-%m-%dT%H:%M:%S%z')
            logging.info(f'Last database record in bucket \'{bucket}\' was at {last_record_date}')
            return last_record_date
        except KeyError:
            logging.warning(f'No data in bucket \'{bucket}\', ingesting from the first file available.')
            return datetime.fromtimestamp(timestamp=0, tz=timezone.utc)
    else:
        raise Exception(f'The following error occurred trying to get last record from DB: {resp.json()}')


@retry(tries=3, delay=10, backoff=1.5, logger=None)
def get_last_record(bucket: str):
    try:
        query_client = influx_client.query_api()
        query = f'from(bucket: "{bucket}") \
            |> range(start: -{BUCKET_LOOKBACK_DAYS}d) \
            |> filter(fn: (r) => r["_measurement"] == "saih") \
            |> keep(columns: ["_time"]) \
            |> sort(columns: ["_time"], desc: true) \
            |> first(column: "_time")'
        
        df = query_client.query_data_frame(query)
        logging.info(f'Last record in database was at {df.at[0, "_time"].strftime("%Y-%m-%dT%H:%M:%S%Z")}')
        return df.at[0, '_time'].to_pydatetime()
    except KeyError:
        logging.warning(f'No data in bucket \'{bucket}\', ingesting from the first file available.')
        return datetime.fromtimestamp(timestamp=0, tz=timezone.utc)
    except Exception as e:
        raise Exception(f'An error occurred trying to access InfluxDB: {e}')


@retry(tries=5, delay=10, backoff=1.5)
def get_all_variables() -> pd.DataFrame:
    resp = requests.post(url=f'{API_URL}/saih/get-variables', json='{}')
    if resp.status_code == 200:
        try:
            df = pd.json_normalize(resp.json()['data'])
            df.drop(columns=['description','measurement_point.denomination','measurement_point.description',
                'measurement_point.location.coordinates','measurement_point.location.type','measurement_point.typology'])
            return df
        except KeyError:
            logging.error(f'No variables found in DB, please check.')
            raise
    else:
        raise Exception(f'The following error occurred trying to get all variables from DB: {resp.json()}')


def get_variable(_df: pd.DataFrame, measurement_point: str, typology: str):
    global last_meas_point, last_typology
    try:
        return _df[(_df['measurement_point.code'] == measurement_point) & (_df['typology'] == typology)]['code'].values[0]
    except IndexError:
        if measurement_point != last_meas_point and typology != last_typology:
            logging.warning(f"{measurement_point} has no variable for typology {typology}!")
            last_meas_point = measurement_point
            last_typology = typology
        return None


def reingest():
    logging.info('### STARTING DISCARDED DATA RE-INGESTION PROCESS ###')
    # period of time to reingest
    range = ceil((datetime.now(tz=timezone.utc) - DATA_SINCE).total_seconds() / 86400) if DATA_SINCE else 60
    # get all raw bucket data
    raw_data = get_raw_data(RAW_DATA_BUCKET, range)
    # get all variable codes from DB
    all_vars_df = get_all_variables()
    
    # get variable code from measurement point code & type
    raw_data['variableCode'] = raw_data.apply(lambda x: get_variable(all_vars_df, x['measurementPointCode'], x['typology']), axis=1)
    # insert data into DB
    saih_data = raw_data.drop(columns=['measurementPointCode', 'typology']).dropna()
    saih_data.set_index('_time', inplace=True)
    saih_data.sort_index(inplace=True)
    write_data(saih_data, BUCKET, MEASUREMENT, ['variableCode'])
    # remove data from raw_data bucket
    logging.info(f'Removing data from bucket {RAW_DATA_BUCKET}...')
    removal_data = raw_data.dropna()
    removal_data.apply(lambda x: delete_data(x['_time'], x['_time'], MEASUREMENT, x['measurementPointCode'], x['typology'], RAW_DATA_BUCKET), axis=1)
    logging.info('### DISCARDED DATA RE-INGESTION FINISHED ###')


def ingest():
    global DATA_PATH
    logging.info('### STARTING INGESTION PROCESS ###')
    # get last record date from DB
    last_record_date = DATA_SINCE if DATA_SINCE else get_last_record(BUCKET)
    # get all variable codes from DB
    all_vars_df = get_all_variables()
    
    # list csv files
    if DATA_ORIGIN == 'ftp':
        if DATA_PATH.endswith((".csv",".CSV")):
            files = [DATA_PATH]
        else:
            files = ftp.list_files(path=DATA_PATH)
            files = [DATA_PATH+file for file in files if file.endswith((".csv",".CSV"))]
    else:
        if os.path.isdir(DATA_PATH):
            files = [DATA_PATH+file for file in os.listdir(DATA_PATH) if file.endswith((".csv",".CSV"))]
        elif os.path.isfile(DATA_PATH):
            files = [DATA_PATH]
            DATA_PATH = os.path.dirname(DATA_PATH) + '/'
            last_record_date = datetime.fromtimestamp(timestamp=0, tz=timezone.utc)
    files.sort()
    logging.debug(f"Partial list of {len(files)} CSV files available in '{DATA_PATH}':\n{files[0:3] + ['...'] + files[-4:-1]}")
    
    # filter & process data from files
    for file in files:
        file_date = None
        # Filename example: CDTI_991231T235959Z.CSV or CDTI_991231235959_00{0-1}.CSV
        for fmt in ("%y%m%dT%H%M%SZ", "%y%m%d%H%M%S_000", "%y%m%d%H%M%S_001"):
            try:
                file_date = pytz.timezone(DATA_TIMEZONE).localize(
                    datetime.strptime(file[len(DATA_PATH)+5:-4], fmt)).astimezone(tz=timezone.utc)
            except ValueError:
                pass
            else:
                break
        
        if file_date and file_date > last_record_date:
            # read & parse data from a selected file
            csv_data = read_data(filename=file)
            csv_data['variableCode'] = csv_data.apply(lambda x: get_variable(all_vars_df, x['measurementPointCode'], x['typology']), axis=1)
            # insert data into DB
            saih_data = csv_data.drop(columns=['measurementPointCode', 'typology', 'unit']).dropna()
            write_data(saih_data, BUCKET, MEASUREMENT, ['variableCode'])
            saih_raw_data = csv_data.loc[(csv_data['variableCode'].notna() == False)].drop(columns=['variableCode', 'unit'])
            write_data(saih_raw_data, RAW_DATA_BUCKET, MEASUREMENT, ['measurementPointCode', 'typology'])
    
    logging.info('### INGESTION PROCESS FINISHED ###')


def exit_handler(*args):
    try:
        logging.info('Exiting...')
        os.unlink(PIDFILE)
        # quit and close the connections
        influx_client.close()
        if DATA_ORIGIN == 'ftp': ftp.disconnect()
    except Exception:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--origin', choices=['ftp', 'file'], default='ftp',
                        help='Origin of data files (default: %(default)s)')
    parser.add_argument('-p', '--path', default='./', help='Path of data files (default: %(default)s)')
    parser.add_argument('-s', '--since', type=lambda x: datetime.strptime(x, '%y%m%dT%H%M%S'),
                        help='Since when to force data ingestion (e.g. %%y%%m%%dT%%H%%M%%S)')
    parser.add_argument('-z', '--timezone', default='UTC', help='Timezone (e.g. \'Europe/Madrid\') \
                        of the data being ingested (default: %(default)s)')
    parser.add_argument('--reingest', action='store_true',
                        help='Start reingestion process of RAW_DATA bucket. \
                            \'origin\', \'path\' & \'timezone\' params do not apply with this option.')
    args = parser.parse_args()
    
    signal.signal(signal.SIGTERM, exit_handler)
    if not check_process(PIDFILE):
        logging.info(f'### STARTING {APPNAME} ###')
        try:
            # Write lock file containing process PID
            print(os.getpid(), file=open(PIDFILE, 'w'))
            DATA_ORIGIN = args.origin
            DATA_PATH = validate_data_path(data_path=args.path, data_origin=DATA_ORIGIN, valid_ext='.csv')
            DATA_TIMEZONE = args.timezone
            DATA_SINCE = pytz.timezone(DATA_TIMEZONE).localize(args.since) if args.since else None
            reingest() if args.reingest else ingest()
        except KeyboardInterrupt:
            pass
        except (Exception, FileNotFoundError) as e:
            logging.error(e)
        finally:
            exit_handler()

