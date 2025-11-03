
import numpy as np

from ..models.demand_unit import DemandUnitModel, demand_units_schema

WATER_COST = {'tipo_agua_superficial': 3000, 'tipo_agua_subterranea': 250000,
              'tipo_agua_reutilizada': 0, 'tipo_agua_trasvase': 150000, 'tipo_agua_desalada': 600000}


def compute(x, uda_hidroeconomic, udi_hidroeconomic, monthly):
    period_factor = 12 if monthly else 365
    if x['tipo_demanda_nombre'] == "UDA":
        return calculate_agriculture_income(x, uda_hidroeconomic[uda_hidroeconomic["uda"] == x["demanda_mi_id"]], period_factor)
    if x['tipo_demanda_nombre'] == "UDRG":
        return calculate_golf_income(x)
    if x['tipo_demanda_nombre'] == "UDU":
        return calculate_urban_income(x)
    if x['tipo_demanda_nombre'] == "HUMEDAL":
        return calculate_wetland_income(x)
    if x['tipo_demanda_nombre'] == "UDI":
        return calculate_industrial_income(x, udi_hidroeconomic[udi_hidroeconomic["udi"] == x["demanda_mi_id"]], period_factor)


def calculate_agriculture_income(x, hydro_economic_df, period_factor, IPC=1.141):
    if x['flow'] == 0 or hydro_economic_df.shape[0] == 0 or x['init_max_flow'] == 0:
        return 0

    water_demand = (x['flow'] / x['init_max_flow']) * \
        hydro_economic_df.iloc[-1]['hm3']
    water_demand_income = np.interp(
        [water_demand], hydro_economic_df['hm3'], hydro_economic_df['cost'])[0] * IPC / period_factor

    # Get water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    return water_demand_income - water_cost


def calculate_golf_income(x, IPC=1.362):
    # Water demand income - We need to convert the flow from hm3 to m3 so we multiply by 1000000
    water_demand_income = x['flow'] * 1000000 * 9.3 * IPC
    # Water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    return water_demand_income - water_cost


def calculate_urban_income(x, IPC=1.061):
    e = -0.15
    P = 3.16 * 1000000  # We need to convert from € / m3 to  € / hm3 so we multiply by 1000000
    D = x['init_max_flow']  # D is a demand
    Q = x['flow']  # Q is a suministred flow
    
    
    # Water demand income
    water_demand_income = 0
    if D != 0 and Q != 0:
        water_demand_income = P * (e - 1) / e * Q + 0.5 * P / e / D * Q ** 2 * IPC

    # Water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    return water_demand_income - water_cost


def calculate_industrial_income(x, hydro_economic_df, period_factor):
    # Water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    if x['demanda_mi_id'] == 'UDI07':
        ipc = 1.088
        # Water demand income
        water_demand_income = x['flow'] * 0.68548718 * 1000 * 1000000 * ipc
        return water_demand_income - water_cost
    else:
        if x['flow'] == 0 or hydro_economic_df.shape[0] == 0:
            return 0
        ipc = 1.141
        water_demand_income = 0
        # Water demand income
        if x['init_max_flow'] != 0:
            water_demand_income = np.interp(
                [x['flow'] / x['init_max_flow']], hydro_economic_df['proportion'], hydro_economic_df['cost'])[0] * ipc / period_factor

        return water_demand_income - water_cost


def calculate_wetland_income(x, period_factor, IPC=1.21):
    wetlands = demand_units_schema.dump(
        DemandUnitModel.get_values('wetland', x['demanda_mi_id']))
    # Calculate income
    cost = 915  # € ha / year
    ipc = 1.21

    for wetland in wetlands:
        return cost * wetland['surface'] * IPC / period_factor
    return 0
