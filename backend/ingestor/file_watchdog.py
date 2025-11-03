import os
import sys
import glob
import json
import time
import dotenv
import signal
import psutil
import logging
import argparse
import requests
import watchdog
import multiprocessing as mp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from watchdog.observers import Observer
from retry.api import retry_call


APPNAME = os.path.basename(__file__).split('.')[0].upper().replace("_", " ")
DOTENV_FILE = os.getenv('DOTENV_FILE', '.env')
dotenv.load_dotenv(DOTENV_FILE)
PIDFILE = f"{os.path.basename(__file__).split('.')[0]}.pid"
DEBUG = os.environ.get('DEBUG', default='False').upper() in ['TRUE', 'YES', '1']
API_URL = os.getenv('API_URL', default='http://api:5000/api')
PROCESS_INTERVAL = int(os.getenv('PROCESS_INTERVAL', default='60')) # seconds

PRODUCTS = {
    'wrf': {
        'filter': 'rect-hourly',
        'url': '/line1/wrf/add-product'
    },
    'wrf-daily': {
        'filter': 'rect-daily',
        'url': '/line1/wrf-daily/add-product'
    },
    'wrf-monthly': {
        'filter': 'MidTerm-WGS84',
        'url': '/line1/wrf-monthly/add-product'
    },
    'exchange': {
        'filter': 'exchange',
        'url': '/line2/exchange/add-product'
    },
    'infiltration': {
        'filter': 'infiltration',
        'url': '/line2/infiltration/add-product'
    },
    'recharge': {
        'filter': 'recharge',
        'url': '/line2/recharge/add-product'
    },
    'water-content': {
        'filter': 'water-content',
        'url': '/line2/water-content/add-product'
    },
    'evapotranspiration': {
        'filter': 'ET_day',
        'url': '/line3/evapotranspiration/add-product'
    },
    'evapotranspiration-monthly': {
        'filter': 'ET_forecast',
        'url': '/line3/evapotranspiration-monthly/add-product'
    },
    'waterdemand': {
        'filter': 'WD_gf',
        'url': '/line3/waterdemand/add-product'
    },
    'waterdemand-monthly': {
        'filter': 'WD_forecast',
        'url': '/line3/waterdemand-monthly/add-product'
    },
    'biomass': {
        'filter': 'biomass',
        'url': '/line3/biomass/add-product'
    },
    'irrigation': {
        'filter': 'irrigation.tif',
        'url': '/line3/irrigation/add-product'
    },
    'irrigation-advice': {
        'filter': 'irrigation_advice.tif',
        'url': '/line3/irrigation-advice/add-product'
    },
    'crop-type': {
        'filter': 'Crop',
        'url': '/line3/crop-type/add-product'
    },
    'DFS0_M11': {
        'filter': 'M11.dfs0',
        'url': '/line2/simulation/add-values'
    },
    'DFS0_SZ': {
        'filter': 'SZ.dfs0',
        'url': '/line2/simulation/add-values'
    }
}

logging.basicConfig(
    format=f'[{APPNAME}]'+' %(asctime)s |%(levelname)s| {%(module)s->%(funcName)s}: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z', level=(logging.DEBUG if DEBUG else logging.INFO))


def check_process(pidfile):
    if os.path.isfile(pidfile):
        with open(pidfile, 'r') as f:
            file_pid = int(f.readline().strip())
        return psutil.pid_exists(file_pid)
    return False


class FileHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, pattern) -> None:
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=[pattern], 
                                                            ignore_directories=True, case_sensitive=False)
        self.filelist = []
    
    def on_closed(self, event):
        logging.debug(f'Watchdog received \'closed\' event for {event.src_path}.')
        self.filelist.append(event.src_path)


def process_list(handler: FileHandler = None, filelist: list = []):
    filelist = handler.filelist.copy() if handler else filelist
    products = []
    
    for file in filelist:
        if DATA_TYPE:
            if PRODUCTS[DATA_TYPE]['filter'] in file:
                products.append((DATA_TYPE, file))
        else:
            for product in PRODUCTS:
                if PRODUCTS[product]['filter'] in file:
                    products.append((product, file))
    
    if len(products) > 0:
        process_pool = mp.Pool(processes=mp.cpu_count() * 10)
        results = process_pool.starmap(func=add_product, iterable=products)
        process_pool.close()
        for result in results:
            if not result:
                products.remove(result[1])
        
        if handler:
            for p in products: handler.filelist.remove(p[1])
        update_ows()
    
    return [file[1] for file in products]


def add_product(product: str, filepath: str):
    filepath = os.path.relpath(filepath, DATA_PATH)
    
    try:
        response = retry_call(requests.get, fargs=[f"{API_URL}/{PRODUCTS[product]['url']}"], 
                            fkwargs={"params": {'file': f'{filepath}'}}, tries=10, delay=10, backoff=2)
        if response.status_code == 200:
            logging.info(f'\'{product}\' product \'{os.path.basename(filepath)}\' correctly added.')
            return_value = True
        else:
            logging.error(f'There was an error adding \'{filepath}\':\n{response.text}')
            return_value = False, (product, filepath)
    except Exception as e:
        logging.error(f'The following error occurred trying to post to {API_URL}: {e}')
        return_value = False, (product, filepath)
    finally:
        return return_value


def update_ows():
    response = requests.get(f'{API_URL}/ows/update-ows/')
    if response.status_code != 200:
        logging.error(f'There was an error updating OWS:\n{response.text}')


def look_for_files(since: datetime = datetime.fromtimestamp(timestamp=0)):
    L1_indexed_files = []; L2_indexed_files = []; L3_indexed_files = []
    L1_current_files = []; L2_current_files = []; L3_current_files = []
    L1_new_files = []; L2_new_files = []; L3_new_files = []
    for x in range((datetime.now() - since).days + 1):
        date = datetime.strftime(since+relativedelta(days=x), "%Y/%m/%d")
        L1_current_files.extend(glob.glob(f'{DATA_PATH}/L1/OUT/**/{date}/*.nc', recursive=True))
        L2_current_files.extend(glob.glob(f'{DATA_PATH}/L2/OUT/**/{date}/*.tif', recursive=True) + 
                                glob.glob(f'{DATA_PATH}/L2/OUT/**/{date}/*.dfs0', recursive=True))
        L3_current_files.extend(glob.glob(f'{DATA_PATH}/L3/OUT/**/{date}/*.tif', recursive=True))
    for x in range(12 * (datetime.now().year - DATA_SINCE.year) + (datetime.now().month - DATA_SINCE.month) + 1):
        date =  datetime.strftime(DATA_SINCE+relativedelta(months=x), "%Y/%m")
        L1_current_files.extend(glob.glob(f'{DATA_PATH}/L1/OUT/**/{date}/*.nc', recursive=True))
        L2_current_files.extend(glob.glob(f'{DATA_PATH}/L2/OUT/**/{date}/*.tif', recursive=True))
        L3_current_files.extend(glob.glob(f'{DATA_PATH}/L3/OUT/**/{date}/*.tif', recursive=True))
    L1_current_files.sort(); L2_current_files.sort(); L3_current_files.sort()
    # Load file lists
    try:
        with open(L1_FILELIST, 'r') as f: L1_indexed_files = json.load(f)
    except FileNotFoundError:
        pass
    try:
        with open(L2_FILELIST, 'r') as f: L2_indexed_files = json.load(f)
    except FileNotFoundError:
        pass
    try:
        with open(L3_FILELIST, 'r') as f: L3_indexed_files = json.load(f)
    except FileNotFoundError:
        pass
    # Compare lists of each line
    L1_new_files = [file for file in L1_current_files if file not in L1_indexed_files]
    L2_new_files = [file for file in L2_current_files if file not in L2_indexed_files]
    L3_new_files = [file for file in L3_current_files if file not in L3_indexed_files]
    # Process new files
    if UPDATE:
        L1_processed_files = [file for file in process_list(filelist=L1_current_files) if file not in L1_indexed_files]
        L2_processed_files = [file for file in process_list(filelist=L2_current_files) if file not in L2_indexed_files]
        L3_processed_files = [file for file in process_list(filelist=L3_current_files) if file not in L3_indexed_files]
    else:
        L1_processed_files = process_list(filelist=L1_new_files)
        L2_processed_files = process_list(filelist=L2_new_files)
        L3_processed_files = process_list(filelist=L3_new_files)
    # Save if different
    for filelist in [(L1_FILELIST,L1_indexed_files,L1_processed_files), 
        (L2_FILELIST,L2_indexed_files,L2_processed_files), (L3_FILELIST,L3_indexed_files,L3_processed_files)]:
        if len(filelist[2]) > 0:
            try:
                with open(filelist[0], 'w') as f: json.dump(filelist[1]+filelist[2], f)
            except Exception as e:
                logging.error(f'An error occurred trying to save {filelist[0]}: {e}')


def observe():
    L1_observer = Observer()
    L2_observer = Observer()
    L3_observer = Observer()
    L1_handler = FileHandler('*.nc')
    L2_handler = FileHandler('*.tif;*.dfs0')
    L3_handler = FileHandler('*.tif')
    L1_observer.schedule(L1_handler, f'{DATA_PATH}/L1/OUT/', recursive=True)
    L2_observer.schedule(L2_handler, f'{DATA_PATH}/L2/OUT/', recursive=True)
    L3_observer.schedule(L3_handler, f'{DATA_PATH}/L3/OUT/', recursive=True)
    L1_observer.start()
    L2_observer.start()
    L3_observer.start()
    try:
        while True:
            time.sleep(PROCESS_INTERVAL)
            process_list(L1_handler)
            process_list(L2_handler)
            process_list(L3_handler)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    finally:
        L1_observer.stop()
        L2_observer.stop()
        L3_observer.stop()
        L1_observer.join()
        L2_observer.join()
        L3_observer.join()


def exit_handler(*args):
    if not mp.parent_process():
        try:
            logging.info(f'Exiting...')
            os.unlink(PIDFILE)
        except Exception:
            pass


if __name__ == "__main__":
    argparge_formatter = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=40)
    parser = argparse.ArgumentParser(formatter_class=argparge_formatter)
    parser.add_argument('action', nargs='?', choices=['watch','observe','list-products'], default='watch',
                        help='''Specify action to perform (default: %(default)s):
 · watch:         Look for files on specified directory.
 · observe:       Watch for file changes using inode system notifications.
 · list-products: List observable product types.''')
    parser.add_argument('-p', '--path', default='./', help='Path of data files (default: %(default)s)')
    parser.add_argument('-s', '--since', default=datetime.fromtimestamp(timestamp=0), 
                        type=lambda x: datetime.strptime(x, '%Y-%m-%d'), help='Since when to look for files (e.g. %%Y-%%m-%%d)')
    parser.add_argument('-t', '--type', default=None, help='Product type to look for. If not specified, all will be taken into account.')
    parser.add_argument('-u', '--update', action='store_true', default=False, help='Force a update of products.')
    args = parser.parse_args()
    ACTION = args.action
    DATA_PATH = args.path
    DATA_SINCE = args.since
    DATA_TYPE = args.type
    UPDATE = args.update
    
    if ACTION == 'list-products':
        print('Watchable product types:')
        for product in PRODUCTS: print(f' · {product}')
        sys.exit()
    
    if not os.path.exists(DATA_PATH):
        sys.exit(f'Please specify a valid path to observe:\n\ti.e.: python {sys.argv[0]} -p /path/to/dir')
    
    if not check_process(PIDFILE):
        logging.info(f'### STARTING {APPNAME} ###')
        try:
            # Write lock file containing process PID
            print(os.getpid(), file=open(PIDFILE, 'w'))
            L1_FILELIST = f'{DATA_PATH}/L1/L1_filelist.json'
            L2_FILELIST = f'{DATA_PATH}/L2/L2_filelist.json'
            L3_FILELIST = f'{DATA_PATH}/L3/L3_filelist.json'
            observe() if ACTION == 'observe' else look_for_files(since=DATA_SINCE)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            logging.error(e)
        finally:
            exit_handler()

