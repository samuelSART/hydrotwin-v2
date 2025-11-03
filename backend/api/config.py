import os
import logging
import sqlalchemy
from dotenv import load_dotenv

# Load .env
load_dotenv()


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('DEBUG', default='').upper() in ['TRUE', 'YES', '1']
    
    logging.basicConfig(
        format='[%(asctime)s] |%(levelname)s| {%(module)s->%(funcName)s}: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %Z',
        level=(logging.DEBUG if DEBUG else logging.INFO))
    
    RDB_HOST = os.getenv('RDB_HOST') or "rdb"
    RDB_PORT = os.getenv('RDB_PORT') or "5432"
    CHS_DB_NAME = os.getenv('CHS_DB_NAME') or "hydrotwin"
    ODC_DB_NAME = os.getenv('ODC_DB_NAME') or "opendatacube"
    CHS_DB_PASSWORD = os.getenv('CHS_DB_PASSWORD') or "chs-db_p4ss"
    ODC_DB_PASSWORD = os.getenv('ODC_DB_PASSWORD') or "odc-db_p4ss"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://{CHS_DB_NAME}:{CHS_DB_PASSWORD}@{RDB_HOST}:{RDB_PORT}/{CHS_DB_NAME}"
    PIEZOMETRY_CORP_DB_URI = sqlalchemy.engine.url.URL.create('mssql+pyodbc', os.getenv('CORP_DB_USER'),
                                                   os.getenv('CORP_DB_PASSWORD'), os.getenv('CORP_DB_HOST'), 1433, os.getenv('PIEZOMETRY_CORP_DB_NAME'))
    COUNTERS_CORP_DB_URI = sqlalchemy.engine.url.URL.create('mssql+pyodbc', os.getenv('CORP_DB_USER'),
                                                   os.getenv('CORP_DB_PASSWORD'), os.getenv('CORP_DB_HOST'), 1433, os.getenv('COUNTERS_CORP_DB_NAME'))
    DROUGHTINDICES_CORP_DB_URI = sqlalchemy.engine.url.URL.create('mssql+pyodbc', os.getenv('CORP_DB_USER'),
                                                   os.getenv('CORP_DB_PASSWORD'), os.getenv('CORP_DB_HOST'), 1433, os.getenv('DROUGHTINDICES_CORP_DB_NAME'))
    SQLALCHEMY_BINDS = {
        'ODC_DB': f"postgresql://{ODC_DB_NAME}:{ODC_DB_PASSWORD}@{RDB_HOST}:{RDB_PORT}/{ODC_DB_NAME}",
        'PIEZOMETRY_DB': f"{PIEZOMETRY_CORP_DB_URI}?driver=ODBC+Driver+18+for+SQL+Server&encrypt=no",
        'COUNTERS_DB': f"{COUNTERS_CORP_DB_URI}?driver=ODBC+Driver+18+for+SQL+Server&encrypt=no",
        'DROUGHTINDICES_DB': f"{DROUGHTINDICES_CORP_DB_URI}?driver=ODBC+Driver+18+for+SQL+Server&encrypt=no"
    }
    
    os.environ["INFLUXDB_V2_TIMEOUT"] = (
        os.environ.get('TIMEOUT') or '30') + '000'
    SAIH_BUCKET = os.environ.get('SAIH_BUCKET') or 'SAIH'
    SIMUL_BUCKET = os.environ.get('SIMUL_BUCKET') or 'SIMUL'
    OWS_URL = os.environ.get('OWS_URL') or 'http://ows:8000/'
    DATA_FOLDER = os.getenv('DATA_FOLDER', default='/geodata/')
    
    DC_CONFIG = {
        'db_database':ODC_DB_NAME,
        'db_hostname':RDB_HOST,
        'db_username':ODC_DB_NAME,
        'db_password':ODC_DB_PASSWORD,
        'db_port':RDB_PORT,
        'index_driver':'default',
        'db_connection_timeout':'60'}
    
    # Authentication
    CAS_AUTH_SERVER = os.getenv('CAS_AUTH_SERVER')
    CAS_SERVICE_URL = os.getenv('CAS_SERVICE_URL') or 'http://localhost:5000/login?next=%2Fprofile'
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'


class TestingConfig(Config):
    TESTING = True
    ENV = 'testing'


class ProductionConfig(Config):
    ENV = 'production'


config = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)
