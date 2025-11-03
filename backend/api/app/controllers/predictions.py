from flask import Blueprint, request, jsonify, current_app, send_file
from owslib.wms import WebMapService
from prophet import Prophet
from datetime import datetime, timedelta
import os
import pandas as pd
import json

from app import influx_client
from app.models.piezometry_value import PiezometerValue, piezometry_values_schema
from app.models.variable import VariableModel
from app.utils.odc_loader import load_geometry_stats
from app.utils.geoutils import find_uda_stats, find_uda_stats_file, find_raster_file
predictions_bp = Blueprint('predictions', __name__)
OWS_URL = current_app.config['OWS_URL']
BUCKET = current_app.config['SAIH_BUCKET']


# FORECAST LENGTH
N_DAYS_15_FORECAST = 15
N_DAYS_1_MONTH = 30
N_MONTHS_7_FORECAST = 7
N_MONTHS_12_FORECAST = 12

# FORECASTING TYPEs
FORECASTING_TYPE_1 = '1'  # 15 days forecasting, daily time step
FORECASTING_TYPE_2 = '2'  # 7 months forecasting, daily time step
FORECASTING_TYPE_3 = '3'  # 7 months forecasting, monthly time step
FORECASTING_TYPE_4 = '4'  # 12 months forecasting, daily time step
FORECASTING_TYPE_5 = '5'  # 12 months forecasting, monthly time step

# Prophet col names
COL_TIEMPO_PROPHATE = 'ds'
COL_VALOR_PROPHATE = 'y'
COL_PREDICTED_Y = 'yhat'
COL_PREDICTION_UNCERTAINTY_LOWER_BOUND = 'yhat_lower'
COL_PREDICTION_UNCERTAINTY_UPPER_BOUND = 'yhat_upper'
COL_PREDICTION_MIN_SATURATION_VALUE = 'floor'
COL_PREDICTION_MAX_SATURATION_VALUE = 'cap'
COL_PREDICTION_MIN_SATURATION_VALUE_PERCENTILE = 0.01
COL_PREDICTION_MAX_SATURATION_VALUE_PERCENTILE = 0.99

# Prophet TIME STEPS
PROPHET_ONE_DAY_TIME_STEP = '1D'
PROPHET_ONE_MONTH_TIME_STEP = '1M'

# Influxdb TIME WINDOWS
INFLUXDB_ONE_DAY_TIME_WINDOW = '1d'
INFLUXDB_ONE_MONTH_TIME_WINDOW = '1mo'

# TRAINING LENGTH
N_DAYS_1_YEAR = 365

LINE_TITLE = {
    "1": "Line-1",
    "2": "Line-2",
    "3": "Line-3"
}


@predictions_bp.route('/get-layers', methods=['GET'])
def get_layers():
    try:
        data = request.args
        line = request.args.get(
            'line') if data is not None and 'line' in data else None
        line = LINE_TITLE[str(line)] if line is not None and str(
            line) in LINE_TITLE else None
        wms = WebMapService(OWS_URL, version='1.3.0')
        data = []
        for layer in list(wms.contents):
            if line is not None:
                if line == wms[layer].parent.title:
                    data.append({
                        "layer": layer,
                        "title": wms[layer].title
                    })
            else:
                data.append({
                    "layer": layer,
                    "title": wms[layer].title
                })
        return jsonify({'status': 200, 'data': data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@predictions_bp.route('/get-styles', methods=['GET'])
def get_styles():
    def format_style(styles):
        data = []
        for style in styles:
            data.append({
                "style": style,
                "title": styles[style]['title']
            })
        return data
    layer = request.args.get('layer')

    try:
        wms = WebMapService(OWS_URL, version='1.3.0')
        styles = format_style(wms[layer].styles)
        data = {
            "styles": styles
        }
        return jsonify({'status': 200, 'data': data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@predictions_bp.route('/get-dates', methods=['GET'])
def get_time():
    layer = request.args.get('layer')
    try:
        wms = WebMapService(OWS_URL, version='1.3.0')
        layer = wms[layer]
        return jsonify({'status': 200, 'data': layer.dimensions['time']['values'], 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500

@predictions_bp.route('/get-uda-stats', methods=['GET'])
def get_uda_stats():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    product = request.args.get('product') if data is not None and 'product' in data else None
    if product is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter product.', 'ok': False}), 400
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except Exception as e:
        return jsonify({'status': 400, 'title': 'Error', 'detail': str(e) + 'Dates must be valid dates in format YYYY-MM-DD hh:mm:ss or YYYY-MM-DD.', 'ok': False}), 400

    try:
        stats = find_uda_stats(date, product)
        if stats is None:
            stats = []
        else:
            if stats.empty:
                print("Dataframe is empty")
                stats = []
            else:
                import random
                stats = stats.set_index("uda")
                stats = stats.to_dict(orient="index")
        return jsonify({'status': 200, 'data': {"values": stats, "bins": []}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500

@predictions_bp.route('/download-uda-stats', methods=['GET'])
def get_uda_stats_file():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    product = request.args.get('product') if data is not None and 'product' in data else None
    if product is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter product.', 'ok': False}), 400
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except Exception as e:
        return jsonify({'status': 400, 'title': 'Error', 'detail': str(e) + 'Dates must be valid dates in format YYYY-MM-DD hh:mm:ss or YYYY-MM-DD.', 'ok': False}), 400

    try:
        file = find_uda_stats_file(date, product)
        if file is None:
            return jsonify({'status': 204, 'data': [], 'ok': True}), 204
        filename = os.path.basename(file)
        return send_file(file, as_attachment=True, attachment_filename=filename), 200
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500

@predictions_bp.route('/download-raster-file', methods=['GET'])
def download_raster_file():
    data = request.args
    date = request.args.get('date') if data is not None and 'date' in data else None
    product = request.args.get('product') if data is not None and 'product' in data else None
    if product is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter product.', 'ok': False}), 400
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except Exception as e:
        return jsonify({'status': 400, 'title': 'Error', 'detail': str(e) + 'Dates must be valid dates in format YYYY-MM-DD hh:mm:ss or YYYY-MM-DD.', 'ok': False}), 400

    try:
        file = find_raster_file(date, product)
        if file is None:
            return jsonify({'status': 204, 'data': [], 'ok': True}), 204
        filename = os.path.basename(file)
        return send_file(file, as_attachment=True, attachment_filename=filename), 200
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@predictions_bp.route('/get-wms-stats', methods=['POST'])
def get_wms_stats():
    data = request.get_json()

    start_datetime = data.get(
        'start-date') if data is not None and 'start-date' in data else None
    end_datetime = data.get(
        'end-date') if data is not None and 'end-date' in data else None
    geometry = data.get(
        'geometry') if data is not None and 'geometry' in data else None
    product = data.get(
        'product') if data is not None and 'product' in data else None
    measurement = data.get(
        'measurement') if data is not None and 'measurement' in data else None
    mean = True

    if product is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameter product, you have to select wrf_s, wrf_m or .', 'ok': False}), 400
    if start_datetime is None or end_datetime is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameters, you have to specify start-datetime and end-datetime.', 'ok': False}), 400

    try:
        datetime.strptime(start_datetime, '%Y-%m-%d')
        datetime.strptime(end_datetime, '%Y-%m-%d')
    except Exception as e:
        return jsonify({'status': 400, 'title': 'Error', 'detail': str(e) + 'Dates must be valid dates in format YYYY-MM-DD hh:mm:ss or YYYY-MM-DD.', 'ok': False}), 400

    try:
        product_query = {
            "time":  (start_datetime, end_datetime),
            "measurements": [measurement]
        }
        resolution = 0.03
        if (geometry["type"] == "Point"):
            resolution = 0.000187

        result, empty = load_geometry_stats(geometry, product=product, output_epsg=4326,
                                            input_epsg=4326, resolution=resolution, product_query=product_query, only_mean=mean)
        if empty:
            return jsonify({'status': 200, 'data': None, 'ok': True})
        return jsonify({'status': 200, 'data': result, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@predictions_bp.route('/variable-prediction', methods=['GET'])
def variable_prediction():
    variable = request.args.get('variable')
    forecasting_type = request.args.get('forecasting')
    database = request.args.get('database')  # odc or corp

    try:
        if variable == None or forecasting_type == None or database == None:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query parameters, you have to specify variable, forecasting, aggregation and database.', 'ok': False}), 400

        df_variables_data = pd.DataFrame()
        if database == 'odc':
            df_variables_data = get_data_from_odc(variable, forecasting_type)
        elif database == 'corp':
            df_variables_data = get_data_from_corp(variable, forecasting_type)
            # IMPORTANTE: para poder hacer el upsample (resample), es necesario que el índice del df sea del tipo datetime
            df_variables_data.set_index(
                keys='_time', drop=True, inplace=True)

            # Make sure there are no duplicates
            df_variables_data.drop_duplicates(inplace=True)

            # Hacemos un upsample de 1 mes con el método 'ffill()'
            df_variables_data_upsampled = df_variables_data.resample(
                '1M').ffill().copy()

            # Hacemos que el índice (ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA) vuelva a ser un campo del df
            df_variables_data_upsampled.reset_index(inplace=True)

            # Reseteamos df_variables_data con df_variables_data_upsampled
            df_variables_data = df_variables_data_upsampled.copy()

        # Check wether or not values were obtained
        if (df_variables_data.shape[0] <= 10):
            # Make an empty dataframe
            df_forecast = pd.DataFrame(columns=[COL_TIEMPO_PROPHATE, COL_PREDICTED_Y, COL_PREDICTION_UNCERTAINTY_LOWER_BOUND,
                                                COL_PREDICTION_UNCERTAINTY_UPPER_BOUND])
            return jsonify({'status': 200, 'data': [], 'ok': True})

        # Just in case, for column influx_column_value, Replace NaN values with 0, although according to the InfluxDB query executed,
        # no NaN values are returned,
        df_variables_data['_value'].fillna(0, inplace=True)

        # Creamos un df de interés con los campos 'ds' y 'y' de Prophet
        df_history_orig = df_variables_data[['_time', '_value']]
        df_history = df_history_orig.rename(
            columns={'_time': COL_TIEMPO_PROPHATE, '_value': COL_VALOR_PROPHATE}, inplace=False)

        # Remove time zone
        df_history[COL_TIEMPO_PROPHATE] = df_history[COL_TIEMPO_PROPHATE].dt.tz_localize(
            None)

        # Specifiy forecaster's min and max SATURATION values, for fitting the model (historical data)
        df_history[COL_PREDICTION_MIN_SATURATION_VALUE] = df_history[COL_VALOR_PROPHATE].quantile(
            COL_PREDICTION_MIN_SATURATION_VALUE_PERCENTILE)
        df_history[COL_PREDICTION_MAX_SATURATION_VALUE] = df_history[COL_VALOR_PROPHATE].quantile(
            COL_PREDICTION_MAX_SATURATION_VALUE_PERCENTILE)

        if df_history[COL_PREDICTION_MAX_SATURATION_VALUE].iloc[0] <= df_history[COL_PREDICTION_MIN_SATURATION_VALUE].iloc[0]:
            return jsonify({'status': 200, 'data': [], 'ok': True})

        # Fit the model
        # modelo = Prophet() # En caso de NO querer saturar, hacerlo así.
        # En caso de SI querer saturar, hacerlo así.
        modelo = Prophet(growth='logistic')
        modelo.fit(df_history)

        # Determine forecasting window
        if (forecasting_type == FORECASTING_TYPE_2):
            n_future_time_steps = N_MONTHS_7_FORECAST * N_DAYS_1_MONTH
            n_future_time_steps_in_days = n_future_time_steps
            forecasting_frequency = PROPHET_ONE_DAY_TIME_STEP
        elif (forecasting_type == FORECASTING_TYPE_3):
            n_future_time_steps = N_MONTHS_7_FORECAST
            n_future_time_steps_in_days = n_future_time_steps * N_DAYS_1_MONTH
            forecasting_frequency = PROPHET_ONE_MONTH_TIME_STEP
        elif (forecasting_type == FORECASTING_TYPE_4):
            n_future_time_steps = N_MONTHS_12_FORECAST * N_DAYS_1_MONTH
            n_future_time_steps_in_days = n_future_time_steps
            forecasting_frequency = PROPHET_ONE_DAY_TIME_STEP
        elif (forecasting_type == FORECASTING_TYPE_5):
            n_future_time_steps = N_MONTHS_12_FORECAST
            n_future_time_steps_in_days = n_future_time_steps * N_DAYS_1_MONTH
            forecasting_frequency = PROPHET_ONE_MONTH_TIME_STEP
        else:
            n_future_time_steps = N_DAYS_15_FORECAST
            n_future_time_steps_in_days = n_future_time_steps
            forecasting_frequency = PROPHET_ONE_DAY_TIME_STEP

        # For BD corporativa, a special treatment is made.
        # En el caso de los datos de la BD corporativa, hay que determinar el SAMPLING RATE en días.
        # para lanzar cotrrectamente el forecasting con Prophet.
        # Determinamos el forecasting_frequency y n_future_time_steps en función de la frecuencia de muestreo
        # de los datos en días.
        # if (database == 'corp'):

        #     # Vamos a calcular el sampign rate (SR) de los datos en días.
        #     # Primero, determinar el periodo de tiempo entre el dato más reciente y el más antiguo.
        #     t1 = df_variables_data.iloc[0]["_time"]
        #     t2 = df_variables_data.iloc[-1]["_time"]

        #     # Ahora calculamos el SR en días
        #     SR = int(abs((t1-t2).days) / df_variables_data.shape[0])

        #     # Si SR <= 1, no cambiamos nada. Si no, nos adaptamos al SR de los datos.
        #     if(SR >= 1):
        #         # Specify forecastint frequency to SR in days
        #         forecasting_frequency = str(SR) + 'D'

        #         # La ventana a predecir nunca será más que el 30% de los datos disponibles en el histórico
        #         n_future_time_steps = min(
        #             int(df_variables_data.shape[0]*0.3), int((N_MONTHS_12_FORECAST * N_DAYS_1_MONTH) / SR))

        # Construct the future time.
        # Si queremos que se muestren los datos del histórico también, indicar include_history=True
        # df_future_time = modelo.make_future_dataframe(periods=n_future_time_steps, freq=forecasting_frequency, include_history=True)

        if (database == 'corp'):
            # Definimos n_future_time_steps y forecasting_frequency para este caso
            n_future_time_steps = N_MONTHS_12_FORECAST
            forecasting_frequency = PROPHET_ONE_MONTH_TIME_STEP

        # Si NO queremos que NO se muestren los datos del histórico, indicar include_history=False
        df_future_time = modelo.make_future_dataframe(
            periods=n_future_time_steps, freq=forecasting_frequency, include_history=False)

        # Specifiy forecaster's min and max SATURATION values, for future prediction values (forecasting)
        df_future_time[COL_PREDICTION_MIN_SATURATION_VALUE] = df_history[COL_VALOR_PROPHATE].quantile(
            COL_PREDICTION_MIN_SATURATION_VALUE_PERCENTILE)
        df_future_time[COL_PREDICTION_MAX_SATURATION_VALUE] = df_history[COL_VALOR_PROPHATE].quantile(
            COL_PREDICTION_MAX_SATURATION_VALUE_PERCENTILE)

        # The predict method will assign each row in future a predicted value which it names yhat. If you pass in historical dates,
        # it will provide an in-sample fit. The forecast object here is a new dataframe that includes a column yhat with the forecast,
        # as well as columns for components and uncertainty intervals.
        df_forecast = modelo.predict(df_future_time)
        # Novedad de v2.0 con respecto a v1.0: limitamos el valor inferior de COL_PREDICTION_UNCERTAINTY_LOWER_BOUND a 0
        df_forecast[COL_PREDICTION_UNCERTAINTY_LOWER_BOUND] = df_forecast[COL_PREDICTION_UNCERTAINTY_LOWER_BOUND].apply(
            lambda x: max(x, 0.0))
        df_forecast[COL_PREDICTED_Y] = df_forecast[COL_PREDICTED_Y].apply(
            lambda x: max(x, 0.0))

        # Return the prediction
        forecast = df_forecast[[COL_TIEMPO_PROPHATE, COL_PREDICTED_Y,
                                COL_PREDICTION_UNCERTAINTY_LOWER_BOUND, COL_PREDICTION_UNCERTAINTY_UPPER_BOUND]].to_json(orient='records')
        return jsonify({'status': 200, 'data': json.loads(forecast), 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


def get_data_from_odc(variable, forecasting_type):
    # Determine N days back for which data will be requested according to the established time period
    training_n_years = 10
    start_time = '-' + str(training_n_years * N_DAYS_1_YEAR) + 'd'

    # Determine aggregation window length according to FORECASTING_TYPE_1 to FORECASTING_TYPE_5 or default
    if (forecasting_type == FORECASTING_TYPE_3) or (forecasting_type == FORECASTING_TYPE_5):
        agregate_window_width = INFLUXDB_ONE_MONTH_TIME_WINDOW
    else:  # Default agregation window
        agregate_window_width = INFLUXDB_ONE_DAY_TIME_WINDOW

    if VariableModel.get_typology(variable) == 'P':
        aggregation_function = 'sum'
    else:
        aggregation_function = 'mean'

    query = f'from(bucket: "{BUCKET}") \
        |> range(start: {start_time}) \
        |> filter(fn: (r) => r._measurement == "saih") \
        |> filter(fn: (r) => r._field == "value") \
        |> filter(fn: (r) => r.variableCode == "{variable}") \
        |> window(every: {agregate_window_width}) \
        |> {aggregation_function}() \
        |> duplicate(column: "_start", as: "_time") \
        |> keep(columns: ["_variableCode", "_time", "_value"])'

    query_client = influx_client.query_api()
    df_variables_data = query_client.query_data_frame(query)

    return df_variables_data


def get_data_from_corp(variable, forecasting_type):

    # define ranges from 10 years ago to now
    d_today = datetime.now()
    training_n_years = 10
    range = {
        'start': (d_today - timedelta(days=training_n_years * N_DAYS_1_YEAR)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end': d_today.strftime('%Y-%m-%dT%H:%M:%SZ')
    }

    # get values from model
    values = piezometry_values_schema.dump(
        PiezometerValue.get_range_values([variable], range['start'], range['end']))

    # create and modify pandas dataframe
    df = pd.DataFrame(values, columns=['variableCode', '_time', '_value'])
    df['_time'] = pd.to_datetime(df['_time'], unit='ms')

    return df
