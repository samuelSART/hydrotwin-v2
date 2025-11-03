import os
from flask import Blueprint, jsonify, current_app, request
from datetime import datetime as dt, timedelta, date
import pandas as pd
import numpy as np
from app import influx_client
import pickle as pkl
import tensorflow as tf
import json

DATA_FOLDER = current_app.config['DATA_FOLDER'] + '/saica/'
FORECAST_CONFIG = {
    1: {
        "in_steps": 30,
        "out_steps": 15,
        "models_folder": "models_hybrid/",
        "scaler_file": "scaler_hybrid.pkl",
        "error_file": "errors_hybrid.pkl",
        "model_file": "Dense.h5"
    },
    6: {
        "in_steps": round(6*30.4167),
        "out_steps": round(6*30.4167),
        "models_folder": "models_hybrid_6month/",
        "scaler_file": "scaler_hybrid_6month.pkl",
        "error_file": "errors_hybrid_6month.pkl",
        "model_file": "DenseDropout.h5"
    }
}
DATA_FILE = DATA_FOLDER + "hybrid_quality_dataset_complete.csv"
ID_FILE = DATA_FOLDER + "ElementosSAIH.XLSX"
SELECTED_STATIONS_FILE = DATA_FOLDER + "selected_stations.pkl"
COMMON_COLS = ["Ordinal", "CodPuntoMedición", "CodTipoPuntoMedición"]
UNUSED_VARS = [
    "TempAgua",
    "Turbidimetro",
    "Amonio",
    "Nitratos",
    "Fosfatos",
    "Presión",
    "VelocidadViento",
    "DireccionViento",
]
PLOT_VARS = ["PH", "Conductividad", "SAC", "OxígenoDisuelto"]

BUCKET = current_app.config['SAIH_BUCKET']
STATION_DATA_IMPUTER = {
    "SAICA Estación Calidad Archena": {
        "SAC": "02Q02E07",
        "Temperatura": "02S01D05",
        "Humedad": "02S01D06",
        "PuntoRocío": "02S01D08"
    },
    "SAICA Estación Calidad Cieza": {
        "Conductividad": "02Q02E03",
        "OxígenoDisuelto": "02Q02E04",
        "SAC": "02Q02E07",
        "Humedad": "02S01D06",
        "PuntoRocío": "02S01D08",
        "Pluviometría": "02A02P01"
    },
    "SAICA Estación Calidad San Antón": {
        "Temperatura": "01A04D05",
        "Humedad": "01A04D06",
        "PuntoRocío": "01A04D08",
        "Pluviometría": "01A04P01"
    }
}


saica_bp = Blueprint('saica', __name__)


def create_df(df, station, station_type, common_cols=COMMON_COLS):
    df = df.copy()
    df = df.loc[df["Denominación"] == station]
    df = df.drop(columns=common_cols)
    df = df.dropna(axis=1, how="all")
    df = df.rename({"Denominación": station_type}, axis=1)
    df = df.reset_index(drop=True)
    return df


def query_data(column_names_dict, start, end):
    query_client = influx_client.query_api()
    df_query = pd.DataFrame()
    for var in column_names_dict:
        try:
            query = f'from(bucket: "{BUCKET}") \
                        |> range(start: time(v: "{start}"), stop: time(v: "{end}")) \
                        |> filter(fn: (r) => r._measurement == "saih") \
                        |> filter(fn: (r) => r._field == "value") \
                        |> filter(fn: (r) => r.variableCode == "{var}") \
                        |> keep(columns: ["_time", "_value", "variableCode"]) \
                        |> aggregateWindow(every: 1h, fn: mean) \
                        |> yield(name: "mean")'
            result = query_client.query_data_frame(query)
            df_query = pd.concat([df_query, result])
        except Exception as e:
            print(f"Error: {e}, var: {var}")
    return df_query


def pivot_df(df, column_names_dict):
    df = df.copy()
    df = df.rename(columns={"_time": "time", "_value": "value"})
    df = df.pivot(index="time", columns="variableCode", values="value")
    df = df.rename(columns=column_names_dict)
    df.columns.name = None
    df.index = df.index.tz_localize(None)
    return df


def clean_df(df):
    df = df.copy()
    df = df.resample("1D").agg(
        {
            "PH": "mean",
            "Conductividad": "mean",
            "OxígenoDisuelto": "mean",
            "SAC": "mean",
            "Temperatura": "mean",
            "Humedad": "mean",
            "PuntoRocío": "mean",
            "Pluviometría": "sum",
        }
    )
    df = df[np.abs(df - df.mean()) <= (3 * df.std())]
    df = df.resample("D").bfill()
    df = df.ffill()
    return df


def create_time_features(df):
    df = df.copy()
    date_time = pd.to_datetime(df.index)
    timestamp_s = date_time.map(pd.Timestamp.timestamp)
    day = 24 * 60 * 60
    year = (365.2425) * day

    df["Dia"] = date_time.day
    df["DiaAño"] = date_time.dayofyear
    df["Mes"] = date_time.month
    df["SemanaAño"] = date_time.weekofyear
    df["Year sin"] = np.sin(timestamp_s * (2 * np.pi / year))
    df["Year cos"] = np.cos(timestamp_s * (2 * np.pi / year))
    return df


def normalize(df, scaler=None):
    df = df.copy()
    df = (df - scaler["train_mean"]) / scaler["train_std"]
    return df


def denormalize(df, scaler=None, var=None):
    df = df.copy()
    if var:
        df = df * scaler["train_std"][var] + scaler["train_mean"][var]
    else:
        df = df * scaler["train_std"] + scaler["train_mean"]
    return df


def init_model(station, forecasting_config):

    results = {
        "column_names_dict": None,
        "scaler": None,
        "model": None,
        "errors": None,
    }

    models_folder = forecasting_config.get("models_folder")
    scaler_file_name = forecasting_config.get("scaler_file")
    error_file_name = forecasting_config.get("error_file")
    model_file = forecasting_config.get("model_file")

    out_folder = DATA_FOLDER + \
        f"hybridQualityForecaster/results/forecasting/{station.replace('SAICA Estación Calidad ', '')}/"
    out_models_folder = out_folder + models_folder
    scaler_file = out_folder + scaler_file_name
    error_file = out_folder + error_file_name

    if os.path.isfile(out_models_folder + model_file) is False:
        return results

    selected_stations = pkl.load(open(SELECTED_STATIONS_FILE, "rb"))
    rawDataVarNames = pd.read_excel(
        ID_FILE, sheet_name="VariablesEnPuntosMed-Tabla", header=1
    )
    df_quality = create_df(rawDataVarNames, station=station,
                           station_type="Q_station")

    df_meteo = create_df(
        rawDataVarNames, station=selected_stations[station]["M"], station_type="M_station")

    df_pluvio = create_df(
        rawDataVarNames, station=selected_stations[station]["P"], station_type="P_station")

    df_station = pd.concat([df_quality, df_meteo, df_pluvio], axis=1)
    df_station = df_station.drop(
        columns=["Q_station", "M_station", "P_station"] + UNUSED_VARS, errors="ignore")

    column_names_dict = None
    column_names_dict = df_station.to_dict("records")[0]
    column_names_dict = {v: k for k, v in column_names_dict.items()}

    if (station in STATION_DATA_IMPUTER):
        column_names_dict_inv = {v: k for k,
                                 v in column_names_dict.items()}
        column_names_dict_inv = {
            **column_names_dict_inv, **STATION_DATA_IMPUTER.get(station)}
        column_names_dict = {v: k for k,
                             v in column_names_dict_inv.items()}

    results["column_names_dict"] = column_names_dict

    scaler = None
    model = None
    errors = None
    scaler = pkl.load(open(scaler_file, "rb"))
    model = tf.keras.models.load_model(out_models_folder + model_file) or None
    errors = pkl.load(open(error_file, "rb"))

    results["scaler"] = scaler
    results["model"] = model
    results["errors"] = errors

    return results


@saica_bp.route('/prediction', methods=['POST'])
def prediction():

    data = request.get_json()

    try:
        station = data.get('station') if data and 'station' in data else None
        target_var = data.get('target') if data and 'target' in data else None
        forecasting = data.get(
            'forecasting') if data and 'forecasting' in data else None

        if station == None or target_var == None or forecasting == None:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing query paramenters, you have to specify station, target variable adn forecasting.', 'ok': False}), 400

        # forecaster config
        forecasting_config = FORECAST_CONFIG.get(forecasting)

        if forecasting_config == None:
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'This forecasting is not available', 'ok': False}), 400

        # init model with selected station
        results = init_model(station, forecasting_config)

        column_names_dict = results["column_names_dict"]
        scaler = results["scaler"]
        model = results["model"]
        errors = results["errors"]

        if(column_names_dict == None or scaler == None or errors.empty == True or model == None):
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'noModel', 'ok': False}), 400

        today = date.today()
        in_steps = forecasting_config.get("in_steps")
        out_steps = forecasting_config.get("out_steps")
        start = (today - timedelta(days=in_steps-1)
                 ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        end = (today + timedelta(days=out_steps)
               ).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        df_query = query_data(column_names_dict, start, end)
        dt.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ') - \
            dt.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
        df_query_pivot = pivot_df(df_query, column_names_dict)

        # clean outliers
        df_query_pivot_clean = clean_df(df_query_pivot)

        # create features
        df_query_pivot_clean = create_time_features(df_query_pivot_clean)
        df_query_pivot_clean = df_query_pivot_clean.reindex(
            columns=scaler["train_mean"].index)

        # df_query_pivot_clean = df_query_pivot_clean.fillna(
        #     df_query_pivot_clean.mean())

        # normalize data
        df_query_pivot_norm = normalize(df_query_pivot_clean, scaler)

        # predict using the model
        num_features = df_query_pivot_norm.shape[1]
        y_pred = model.predict(
            df_query_pivot_norm[:today].values.reshape(
                1, -1, num_features)
        )[0]
        y_actual = df_query_pivot_clean.resample("1D").mean()
        y_pred = pd.DataFrame(
            y_pred, columns=df_query_pivot_norm.columns, index=y_actual[in_steps:].index)
        print(
            f"y_pred_size: {y_pred.shape}, y_actual_size: {y_actual[in_steps:].shape}")

        # invert normalization
        y_pred_inv = denormalize(y_pred, scaler)

        # error dataframe
        df_error = pd.DataFrame({})
        for var in scaler["train_mean"].index:
            df_error[var] = errors[errors["variable"] == var].filter(
                like="error_day").describe().T["mean"]

        # format result
        if((target_var in y_pred_inv) == False):
            return jsonify({'status': 400, 'title': 'Error', 'detail': 'noVariable', 'ok': False}), 400

        result = y_pred_inv[target_var].reset_index()
        upper_bound = y_pred[target_var].values + \
            abs(df_error[target_var].values)
        lower_bound = y_pred[target_var].values - \
            abs(df_error[target_var].values)
        result["yhat_upper"] = denormalize(upper_bound, scaler, target_var)
        result["yhat_lower"] = denormalize(lower_bound, scaler, target_var)
        result = result.rename(columns={"time": "ds", target_var: "yhat"})

        return jsonify({'status': 200, 'data': json.loads(result.to_json(orient="records")), 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'text': str(e), 'ok': False}), 500
