from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from influxdb_client import InfluxDBClient

from config import config


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
influx_client = InfluxDBClient.from_env_properties()


def create_app(config_name):
    """Construct the core app object."""
    app = Flask(__name__)
    CORS(app)

    # Application Configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # Add HierarchyId (MSSql specific ODBC type -151) handler to PIEZOMETRY_DB bindded engine
    # (not needed if no Geometry type column is mapped)
    # https://github.com/mkleehammer/pyodbc/issues/404#issuecomment-603801417
    # db.get_engine(app, bind='PIEZOMETRY_DB').connect().connection.add_output_converter(-151, lambda x: str(x))

    # Blueprint register
    with app.app_context():
        from .utils.swagger import SWAGGER_BLUEPRINT, SWAGGER_URL
        from .controllers.auth import auth_bp
        from .controllers.saih import saih_bp
        from .controllers.demand_unit import demand_unit_bp
        from .controllers.water_body import water_body_bp
        from .controllers.environmental_flow import environmental_flow_bp
        from .controllers.dam import dam_bp
        from .controllers.co2 import co2_bp
        from .controllers.errors import errors_bp
        from .controllers.line5 import line5_bp
        from .controllers.line4 import line4_bp
        from .controllers.line3 import line3_bp
        from .controllers.line2 import line2_bp
        from .controllers.line1 import line1_bp
        from .controllers.predictions import predictions_bp
        from .controllers.ows import ows_bp
        from .controllers.piezometry import piezometry_bp
        from .controllers.hydro_economic import hydro_economic_bp
        from .controllers.saica import saica_bp
        from .controllers.version import version_bp
        from .controllers.healthcheck import healthcheck_bp
        from .controllers.errors import errors_bp
        from .controllers.water_meters import water_meters_bp
        from .controllers.drought_indices import drought_indices_bp
        from .controllers.system_unit import system_unit_bp
        app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(saih_bp, url_prefix='/api/saih')
        app.register_blueprint(line5_bp, url_prefix='/api/line5')
        app.register_blueprint(line4_bp, url_prefix='/api/line4')
        app.register_blueprint(line3_bp, url_prefix='/api/line3')
        app.register_blueprint(line2_bp, url_prefix='/api/line2')
        app.register_blueprint(line1_bp, url_prefix='/api/line1')
        app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
        app.register_blueprint(demand_unit_bp, url_prefix='/api/demand-unit')
        app.register_blueprint(water_body_bp, url_prefix='/api/water-body')
        app.register_blueprint(ows_bp, url_prefix='/api/ows')
        app.register_blueprint(environmental_flow_bp,
                               url_prefix='/api/environmental-flow')
        app.register_blueprint(dam_bp, url_prefix='/api/dam')
        app.register_blueprint(piezometry_bp, url_prefix='/api/corporate')
        app.register_blueprint(saica_bp, url_prefix='/api/saica')
        app.register_blueprint(co2_bp, url_prefix='/api/co2')
        app.register_blueprint(
            hydro_economic_bp, url_prefix='/api/hydro-economic')
        app.register_blueprint(water_meters_bp, url_prefix='/api/water-meters')
        app.register_blueprint(version_bp, url_prefix='/api/version')
        app.register_blueprint(drought_indices_bp, url_prefix='/api/drought-indices')
        app.register_blueprint(system_unit_bp, url_prefix='/api/system-unit')
        app.register_blueprint(healthcheck_bp, url_prefix='/healthcheck')
        app.register_blueprint(errors_bp)
    return app
