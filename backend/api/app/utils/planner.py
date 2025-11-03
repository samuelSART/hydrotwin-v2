
import os
import json
import hashlib
import logging
import pandas as pd
from flask import current_app
from datetime import datetime

from . import modelo_L4_L5 as modelo
from . import hidroeconomic


DATA_FOLDER = current_app.config['DATA_FOLDER']
PLAN_FOLDER = DATA_FOLDER + '/L4/OUT/'
CO2_EMISSION_FILE = DATA_FOLDER + '/L4/CO2_emission.csv'
UDA_ECONOMIC_FILE = DATA_FOLDER + '/L4/agricultureEconomic.csv'
UDI_ECONOMIC_FILE = DATA_FOLDER + '/L4/industryEconomic.csv'
PIDFILE = PLAN_FOLDER + "/planner.pid"


# CO2 of each water origin type kW/m3
water_CO2 = {
    "superficial": 0.06,
    "subterranea": 0.9,
    "reutilizada": 0.78,
    "trasvase": 1.21,
    "desalada": 4.32
}

# t CO2 / kW
emission_factor = 0.000354


ud_types_CO2 = {
    "UDU": 17.432137489428,  # t CO2 / hm3,
    "UDI": {  # t C02 / hm3
        "UDI01": 692074,
        "UDI02": 1211850,
        "UDI03": 372821,
        "UDI04": 478388,
        "UDI05": 799353,
        "UDI06": 386516,
        "UDI07": 168925,
    },
    "UDRG": 692.67920511001,  # t CO2 / hm3

    "AMBIENTAL": -395.2  # t CO2 / hm3

}


def compute_hash(file):
    if not os.path.isfile(file):
        return None
    h = hashlib.sha1()
    with open(file, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()


def read_type_table(file, type, monthly):
    df = pd.read_csv(file)
    return process_table(df[df["tipo_demanda_nombre"] == type], "demanda_mi_id", monthly)


def read_table(file, monthly):
    df = pd.read_csv(file)
    return process_table(df, "tipo_demanda_nombre", monthly)


def process_table(df, column, monthly: bool = False):
    emission_df = pd.read_csv(CO2_EMISSION_FILE)
    uda_hidroeconomic = pd.read_csv(UDA_ECONOMIC_FILE)
    udi_hidroeconomic = pd.read_csv(UDI_ECONOMIC_FILE)

    dates = df["timestamp"].unique()
    df = df.sort_values([column])
    names = df[column].unique()
    emission_column = "daily"
    if monthly:
        emission_column = "monthly"

    data = []
    for name in names:
        aux_df = df[df[column] == name]
        aux_df = aux_df.sort_values(["timestamp"])
        demand = aux_df["init_max_flow"].sum()
        planned = aux_df["flow"].sum()
        aux_df_groupby = aux_df.groupby("timestamp")
        deficitPerDay = aux_df_groupby.apply(
            lambda x: x["flow"].sum() - x["init_max_flow"].sum()).values
        superficial = float(aux_df_groupby.apply(
            lambda x: (x["flow"] * x["tipo_agua_superficial"]).sum()).sum())
        subterranea = float(aux_df_groupby.apply(
            lambda x: (x["flow"] * x["tipo_agua_subterranea"]).sum()).sum())
        reutilizada = float(aux_df_groupby.apply(
            lambda x: (x["flow"] * x["tipo_agua_reutilizada"]).sum()).sum())
        trasvase = float(aux_df_groupby.apply(
            lambda x: (x["flow"] * x["tipo_agua_trasvase"]).sum()).sum())
        desalada = float(aux_df_groupby.apply(
            lambda x: (x["flow"] * x["tipo_agua_desalada"]).sum()).sum())
        dinamic_emission = ((superficial * water_CO2["superficial"]) + (subterranea * water_CO2["subterranea"]) + (
            reutilizada * water_CO2["reutilizada"]) + (trasvase * water_CO2["trasvase"]) + (desalada * water_CO2["desalada"])) * emission_factor

        emission = aux_df.apply(lambda x: compute_CO2_uda(dinamic_emission, emission_df[emission_df["id"] == x["demanda_mi_id"]][emission_column]) if (
            x["tipo_demanda_nombre"] == "UDA") else compute_CO2_other(dinamic_emission, x['flow'], x['demanda_mi_id'], x['tipo_demanda_nombre']), axis=1).sum()

        economical = aux_df.apply(lambda x: hidroeconomic.compute(
            x, uda_hidroeconomic, udi_hidroeconomic, monthly), axis=1).sum()

        data.append({
            "name": name,
            "demand": round(float(demand), 4),
            "planned": round(float(planned), 4),
            "dates": list(dates),
            "deficit": round(float(planned - demand), 4),
            "deficitPerDay": list(map(float, deficitPerDay)),
            "superficial": round(superficial, 4),
            "subterranea": round(subterranea, 4),
            "reutilizada": round(reutilizada, 4),
            "trasvase": round(trasvase, 4),
            "desalada": round(desalada, 4),
            "emission": round(float(emission), 0),
            "economical": round(float(economical), 0)
        })
    return data


def read_unit_plot(file, id, monthly):
    df = pd.read_csv(file)
    return process_plot(df[df["demanda_mi_id"] == id], monthly)


def read_type_plot(file, type, monthly):
    df = pd.read_csv(file)
    return process_plot(df[df["tipo_demanda_nombre"] == type], monthly)


def read_plot(file, monthly):
    df = pd.read_csv(file)
    return process_plot(df, monthly)


def process_plot(df, monthly: bool = False):
    emission = pd.read_csv(CO2_EMISSION_FILE)
    uda_hidroeconomic = pd.read_csv(UDA_ECONOMIC_FILE)
    udi_hidroeconomic = pd.read_csv(UDI_ECONOMIC_FILE)

    dates = df["timestamp"].sort_values().unique()
    demand = []
    planned = []
    incert_low = []
    incert_high = []
    co2 = []
    economic = []
    superficial = []
    subterranea = []
    reutilizada = []
    trasvase = []
    desalada = []

    emission_column = "daily"
    if monthly:
        emission_column = "monthly"

    for date in dates:
        aux_df = df[df['timestamp'] == date].copy()
        demand.append(float(aux_df["init_max_flow"].sum()))
        planned_flow = float(aux_df["flow"].sum())
        incert_low.append(float(aux_df["flow_incert_low"].sum()))
        incert_high.append(float(aux_df["flow_incert_high"].sum()))
        planned.append(planned_flow)
        aux_df["superficial"] = aux_df["flow"] * \
            aux_df["tipo_agua_superficial"]
        aux_df["total_CO2"] = (aux_df["superficial"] *
                               water_CO2["superficial"])

        aux_df["subterranea"] = aux_df["flow"] * \
            aux_df["tipo_agua_subterranea"]
        aux_df["total_CO2"] = aux_df["total_CO2"] + \
            (aux_df["subterranea"] * water_CO2["subterranea"])

        aux_df["reutilizada"] = aux_df["flow"] * \
            aux_df["tipo_agua_reutilizada"]
        aux_df["total_CO2"] = aux_df["total_CO2"] + \
            (aux_df["reutilizada"] * water_CO2["reutilizada"])

        aux_df["trasvase"] = aux_df["flow"] * aux_df["tipo_agua_trasvase"]
        aux_df["total_CO2"] = aux_df["total_CO2"] + \
            (aux_df["trasvase"] * water_CO2["trasvase"])

        aux_df["desalada"] = aux_df["flow"] * aux_df["tipo_agua_desalada"]
        aux_df["total_CO2"] = aux_df["total_CO2"] + \
            (aux_df["desalada"] * water_CO2["desalada"])

        aux_df["total_CO2"] = aux_df["total_CO2"] * emission_factor

        aux_df["CO2"] = aux_df.apply(lambda x: compute_CO2_uda(x["total_CO2"], emission[emission["id"] == x["demanda_mi_id"]][emission_column]) if (
            x["tipo_demanda_nombre"] == "UDA") else compute_CO2_other(x["total_CO2"], x['flow'], x['demanda_mi_id'], x['tipo_demanda_nombre']), axis=1)

        aux_df["Hidroeconomic"] = aux_df.apply(lambda x: hidroeconomic.compute(
            x, uda_hidroeconomic, udi_hidroeconomic, monthly), axis=1)

        if planned_flow != 0:
            superficial.append(aux_df["superficial"].sum() / planned_flow)
            subterranea.append(aux_df["subterranea"].sum() / planned_flow)
            reutilizada.append(aux_df["reutilizada"].sum() / planned_flow)
            trasvase.append(aux_df["trasvase"].sum() / planned_flow)
            desalada.append(aux_df["desalada"].sum() / planned_flow)
        else:
            superficial.append(0)
            subterranea.append(0)
            reutilizada.append(0)
            trasvase.append(0)
            desalada.append(0)

        co2.append(float(aux_df["CO2"].sum()))
        economic.append(float(aux_df["Hidroeconomic"].sum()))

    return {
        "date": dates.tolist(),
        "demand": demand,
        "planned": planned,
        "incertLow": incert_low,
        "incertHigh": incert_high,
        "subterranea": subterranea,
        "superficial": superficial,
        "reutilizada": reutilizada,
        "trasvase": trasvase,
        "desalada": desalada,
        "CO2": co2,
        "economic": economic
    }


def compute_CO2_uda(dinamic_co2, static_co2):
    if static_co2.shape[0] == 0:
        return dinamic_co2
    return static_co2.iloc[0] + dinamic_co2


def compute_CO2_other(dinamic_co2, flow, id, type):
    static_co2 = 0
    if type in ud_types_CO2:
        if type == "UDI":
            if id in ud_types_CO2[type]:
                static_co2 = ud_types_CO2[type][id] * flow
        else:
            static_co2 = ud_types_CO2[type] * flow
    return static_co2 + dinamic_co2


def generate_plan(superficial: float = 1.0, subterranea: float = 1.0, reutilizada: float = 1.0,
                  trasvase: float = 1.0, desalada: float = 1.0, monthly: bool = False, daily: bool = False):
    try:
        # Write lock file containing process PID:
        print(os.getpid(), file=open(PIDFILE, 'w'))

        today = pd.to_datetime("today").date()
        if monthly:
            end = today + pd.tseries.offsets.DateOffset(months=7)
        else:
            end = today + pd.tseries.offsets.DateOffset(days=14)

        simulation_step = 1
        if monthly:
            if not daily:
                simulation_step = 2

        df = modelo.Planificar_Optimizar_Suministros_a_Demandas(
            p_simulation_type=1,
            p_simulation_step=simulation_step,
            p_date_init=today.strftime("%Y-%m-%d"),
            p_date_end=end.strftime("%Y-%m-%d"),
            p_percent_agua_superficial=float(superficial),
            p_percent_agua_subterranea=float(subterranea),
            p_percent_agua_reutilizada=float(reutilizada),
            p_percent_agua_trasvase=float(trasvase),
            p_percent_agua_desalada=float(desalada),
        )

        data = {
            "superficial": superficial,
            "subterranea": subterranea,
            "reutilizada": reutilizada,
            "trasvase": trasvase,
            "desalada": desalada,
            "CO2impact": 0,
            "economicImpact": 0,
            "waterDeficit": 1,
            "start": today.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "creationDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if monthly:
            if daily:
                json_file = PLAN_FOLDER+"/SIMUL_M/last_daily_plan_data.json"
            else:
                json_file = PLAN_FOLDER+"/SIMUL_M/last_monthly_plan_data.json"
        else:
            json_file = PLAN_FOLDER+"/SIMUL_S/last_daily_plan_data.json"

        if monthly:
            if daily:
                file = PLAN_FOLDER+"/SIMUL_M/last_daily.csv"
            else:
                file = PLAN_FOLDER+"/SIMUL_M/last_monthly.csv"
        else:
            file = PLAN_FOLDER+"SIMUL_S/last_daily.csv"

        if monthly:
            if not os.path.exists(PLAN_FOLDER+"/SIMUL_M/"):
                os.makedirs(PLAN_FOLDER+"/SIMUL_M/")
        else:
            if not os.path.exists(PLAN_FOLDER+"/SIMUL_S/"):
                os.makedirs(PLAN_FOLDER+"/SIMUL_S/")

        with open(json_file, 'w') as f:
            json.dump(data, f)

        df.to_csv(file, index=False)
    except Exception as e:
        logging.error(f'An error occurred generating a plan: {e}')
    finally:
        os.unlink(PIDFILE)
