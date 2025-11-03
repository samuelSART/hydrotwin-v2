
import os
import json
import logging
import pandas as pd
from datetime import datetime
from flask import current_app

from . import planner
from . import hidroeconomic
from . import modelo_L4_L5 as modelo


DATA_FOLDER = current_app.config['DATA_FOLDER']
OPTIMIZED_PLAN_FOLDER = DATA_FOLDER + '/L5/OUT/'
CO2_EMISSION_FILE = DATA_FOLDER + '/L4/CO2_emission.csv'
UDA_ECONOMIC_FILE = DATA_FOLDER + '/L4/agricultureEconomic.csv'
UDI_ECONOMIC_FILE = DATA_FOLDER + '/L4/industryEconomic.csv'
PIDFILE = OPTIMIZED_PLAN_FOLDER + "/optimizer.pid"


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


def read_unit_plot(file, old_plan_file, id, monthly):
    df = pd.read_csv(file)
    optimized_data = planner.process_plot(
        df[df["demanda_mi_id"] == id], monthly)
    if old_plan_file:
        old_plan = pd.read_csv(old_plan_file)
        old_plan = old_plan[old_plan["demanda_mi_id"] == id]
        old_plan_data = process_old_plan_plot(
            old_plan, optimized_data["date"], monthly)
    else:
        old_plan_data = None
    optimized_data["oldPlan"] = old_plan_data
    return optimized_data


def read_type_plot(file, old_plan_file, type, monthly):
    df = pd.read_csv(file)
    optimized_data = planner.process_plot(
        df[df["tipo_demanda_nombre"] == type], monthly)
    if old_plan_file:
        old_plan = pd.read_csv(old_plan_file)
        old_plan = old_plan[old_plan["tipo_demanda_nombre"] == type]
        old_plan_data = process_old_plan_plot(
            old_plan, optimized_data["date"], monthly)
    else:
        old_plan_data = None
    optimized_data["oldPlan"] = old_plan_data
    return optimized_data


def read_plot(file, old_plan_file, monthly):
    df = pd.read_csv(file)
    optimized_data = planner.process_plot(df, monthly)
    if old_plan_file:
        old_plan = pd.read_csv(old_plan_file)
        old_plan_data = process_old_plan_plot(
            old_plan, optimized_data["date"], monthly)
    else:
        old_plan_data = None
    optimized_data["oldPlan"] = old_plan_data
    return optimized_data


def process_old_plan_plot(df, dates, monthly: bool = False):

    emission = pd.read_csv(CO2_EMISSION_FILE)
    uda_hidroeconomic = pd.read_csv(UDA_ECONOMIC_FILE)
    udi_hidroeconomic = pd.read_csv(UDI_ECONOMIC_FILE)

    demand = []
    planned = []
    co2 = []
    economic = []

    emission_column = "daily"
    if monthly:
        emission_column = "monthly"

    for date in dates:
        aux_df = df[df['timestamp'] == date].copy()
        if aux_df.shape[0] == 0:
            demand.append(0)
            planned.append(0)
            co2.append(0)
            economic.append(0)
            continue

        demand.append(float(aux_df["init_max_flow"].sum()))
        planned_flow = float(aux_df["flow"].sum())
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

        co2.append(round(float(aux_df["CO2"].sum()), 0))
        economic.append(round(float(aux_df["Hidroeconomic"].sum()), 0))

    return {
        "demand": demand,
        "planned": planned,
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


def generate_optimzied_plan(superficial: float = 1.0, subterranea: float = 1.0, reutilizada: float = 1.0,  trasvase: float = 1.0, desalada: float = 1.0,
                            waterDeficit: float = 1.0, CO2impact: float = 1.0,  economicImpact: float = 1.0,  monthly: bool = False, daily: bool = False):
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
            p_simulation_type=2,
            p_simulation_step=simulation_step,
            p_date_init=today.strftime("%Y-%m-%d"),
            p_date_end=end.strftime("%Y-%m-%d"),
            p_percent_agua_superficial=superficial,
            p_percent_agua_subterranea=subterranea,
            p_percent_agua_reutilizada=reutilizada,
            p_percent_agua_trasvase=trasvase,
            p_percent_agua_desalada=desalada,
            p_peso_deficit=waterDeficit,
            p_peso_co2=CO2impact,
            p_peso_economic=economicImpact,
        )

        data = {
            "superficial": superficial,
            "subterranea": subterranea,
            "reutilizada": reutilizada,
            "trasvase": trasvase,
            "desalada": desalada,
            "CO2impact": CO2impact,
            "economicImpact": economicImpact,
            "waterDeficit": waterDeficit,
            "start": today.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "creationDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if monthly:
            if daily:
                json_file = OPTIMIZED_PLAN_FOLDER+"/SIMUL_M/last_daily_optimized_plan_data.json"
            else:
                json_file = OPTIMIZED_PLAN_FOLDER+"/SIMUL_M/last_monthly_optimized_plan_data.json"
        else:
            json_file = OPTIMIZED_PLAN_FOLDER+"/SIMUL_S/last_daily_optimized_plan_data.json"

        if monthly:
            if daily:
                file = OPTIMIZED_PLAN_FOLDER+"/SIMUL_M/last_daily.csv"
            else:
                file = OPTIMIZED_PLAN_FOLDER+"/SIMUL_M/last_monthly.csv"
        else:
            file = OPTIMIZED_PLAN_FOLDER+"SIMUL_S/last_daily.csv"

        if monthly:
            if not os.path.exists(OPTIMIZED_PLAN_FOLDER+"/SIMUL_M/"):
                os.makedirs(OPTIMIZED_PLAN_FOLDER+"/SIMUL_M/")
        else:
            if not os.path.exists(OPTIMIZED_PLAN_FOLDER+"/SIMUL_S/"):
                os.makedirs(OPTIMIZED_PLAN_FOLDER+"/SIMUL_S/")

        with open(json_file, 'w') as f:
            json.dump(data, f)

        df.to_csv(file, index=False)
    except Exception as e:
        logging.error(f'An error occurred generating an optimized plan: {e}')
    finally:
        os.unlink(PIDFILE)

