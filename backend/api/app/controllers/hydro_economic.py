from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import numpy as np
import json

from ..models.demand_unit import DemandUnitModel, demand_units_schema

hydro_economic_bp = Blueprint('hydro_economic', __name__)

# Water cost is in €/hm3
WATER_COST = {'tipo_agua_superficial': 3000, 'tipo_agua_subterranea': 250000,
              'tipo_agua_reutilizada': 0, 'tipo_agua_trasvase': 150000, 'tipo_agua_desalada': 600000}


@hydro_economic_bp.route('/get-agriculture-income', methods=['GET'])
def get_agriculture_income():
    line = request.args.get('line')
    period = request.args.get('period')

    try:
        # Read planification or optimization data
        try:
            if period == 'daily':
                period_factor = 365
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_S/last_daily.csv', index_col=[0])
            elif period == 'monthlyDaily':
                period_factor = 12
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_daily.csv', index_col=[0])
            elif period == 'monthlyMonthly':
                period_factor = 12
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_monthly.csv', index_col=[0])
            else:
                raise Exception('Period not supported')
        except Exception as e:
            raise Exception(f'Error reading {line} with period {period} data')

        # Filter by demand type
        uda_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'UDA')]
        # Get simulation flow and flow max mean
        uda_simulation_df = uda_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Get proportion of use flow
        uda_simulation_df['proportion'] = uda_simulation_df['flow'].divide(
            uda_simulation_df['init_max_flow'])
        # Fill NaN values with 0
        uda_simulation_df.fillna(
            uda_simulation_df[['proportion', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Read hydro-economic data
        hydro_economic_df = pd.read_csv(
            current_app.config['DATA_FOLDER'] + f'/{line}/agricultureEconomic.csv')
        # Calculate income
        ipc = 1.141
        uda_simulation_df['income'] = uda_simulation_df.apply(
            lambda x: calculate_agriculture_income(x, hydro_economic_df[hydro_economic_df['uda'] == x['demanda_mi_id']], ipc, period_factor), axis=1)
        # Rename demanda_mi_id to uda
        uda_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)
        # Generate bins
        bins = pd.qcut(
            uda_simulation_df['income'], q=4, retbins=True, duplicates='drop')[1]

        return jsonify({'status': 200, 'data': {'bins': bins.tolist(), 'hydroEconomic': json.loads(uda_simulation_df[['code', 'income']].to_json(orient='records'))},  'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


def calculate_agriculture_income(x, hydro_economic_df, ipc, period_factor):
    if x['proportion'] == 0 or hydro_economic_df.shape[0] == 0:
        return 0

    # Water demand income
    water_demand = x['proportion'] * hydro_economic_df.iloc[-1]['hm3']
    water_demand_income = np.interp(
        [water_demand], hydro_economic_df['hm3'], hydro_economic_df['cost'])[0] * ipc / period_factor

    # Get water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    return water_demand_income - water_cost


@hydro_economic_bp.route('/get-golf-income', methods=['GET'])
def get_golf_income():
    line = request.args.get('line')
    period = request.args.get('period')

    try:
        # Read planification or optimization data
        try:
            if period == 'daily':
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_S/last_daily.csv', index_col=[0])
            elif period == 'monthlyDaily':
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_daily.csv', index_col=[0])
            elif period == 'monthlyMonthly':
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_monthly.csv', index_col=[0])
            else:
                raise Exception('Period not supported')
        except Exception as e:
            raise Exception(f'Error reading {line} with period {period} data')
        # Filter by demand type
        udrg_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'UDRG')]
        # Get simulation flow and flow max mean
        udrg_simulation_df = udrg_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        udrg_simulation_df.fillna(
            udrg_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Calculate income per UDRG
        ipc = 1.362
        udrg_simulation_df['income'] = udrg_simulation_df.apply(
            lambda x: calculate_golf_income(x, ipc), axis=1)
        # Rename demanda_mi_id to uda
        udrg_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)
        # Generate bins
        bins = pd.qcut(
            udrg_simulation_df['income'], q=4, retbins=True, duplicates='drop')[1]

        return jsonify({'status': 200, 'data': {'bins': bins.tolist(), 'hydroEconomic': json.loads(udrg_simulation_df[['code', 'income']].to_json(orient='records'))}, 'ok': True})

    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


def calculate_golf_income(x, ipc):
    # Water demand income - We need to convert the flow from hm3 to m3 so we multiply by 1000000
    water_demand_income = x['flow'] * 1000000 * 9.3 * ipc
    # Water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    return water_demand_income - water_cost


@hydro_economic_bp.route('/get-urban-income', methods=['GET'])
def get_urban_income():
    line = request.args.get('line')
    period = request.args.get('period')

    try:
        # Read planification or optimization data
        try:
            if period == 'daily':
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_S/last_daily.csv', index_col=[0])
            elif period == 'monthlyDaily':
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_daily.csv', index_col=[0])
            elif period == 'monthlyMonthly':
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_monthly.csv', index_col=[0])
            else:
                raise Exception('Period not supported')
        except Exception as e:
            raise Exception(f'Error reading {line} with period {period} data')
        # Filter by demand type
        udu_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'UDU')]
        # Get simulation flow and flow max mean
        udu_simulation_df = udu_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        udu_simulation_df.fillna(
            udu_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Calculate income
        ipc = 1.061
        udu_simulation_df['income'] = udu_simulation_df.apply(
            lambda x: calculate_urban_income(x, ipc), axis=1)
        udu_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)
        # Generate bins
        bins = pd.qcut(
            udu_simulation_df['income'], q=4, retbins=True, duplicates='drop')[1]

        return jsonify({'status': 200, 'data': {'bins': bins.tolist(), 'hydroEconomic': json.loads(udu_simulation_df[['code', 'income']].to_json(orient='records'))}, 'ok': True})

    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


def calculate_urban_income(x, ipc):
    e = -0.15
    P = 3.16 * 1000000  # We need to convert from € / m3 to  € / hm3 so we multiply by 1000000
    D = x['init_max_flow']  # D is a demand
    Q = x['flow']  # Q is a suministred flow

    # Water demand income
    water_demand_income = P * (e - 1) / e * Q + 0.5 * P / e / D * Q ** 2 * ipc

    # Water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])

    return water_demand_income - water_cost


@hydro_economic_bp.route('/get-industry-income', methods=['GET'])
def get_industrial_income():
    line = request.args.get('line')
    period = request.args.get('period')

    try:
        # Read planification or optimization data
        try:
            if period == 'daily':
                period_factor = 365
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_S/last_daily.csv', index_col=[0])
            elif period == 'monthlyDaily':
                period_factor = 12
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_daily.csv', index_col=[0])
            elif period == 'monthlyMonthly':
                period_factor = 12
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_monthly.csv', index_col=[0])
            else:
                raise Exception('Period not supported')
        except Exception as e:
            raise Exception(f'Error reading {line} with period {period} data')
        # Filter by demand type
        udi_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'UDI')]
        # Get simulation flow and flow max mean
        udi_simulation_df = udi_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Get proportion of use flow
        udi_simulation_df['proportion'] = udi_simulation_df['flow'].divide(
            udi_simulation_df['init_max_flow'])
        # Fill NaN values with 0
        udi_simulation_df.fillna(
            udi_simulation_df[['proportion', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Read hydro-economic data
        hydro_economic_df = pd.read_csv(
            current_app.config['DATA_FOLDER'] + f'/{line}/industryEconomic.csv')
        # Calculate income
        udi_simulation_df['income'] = udi_simulation_df.apply(
            lambda x: calculate_industrial_income(x, hydro_economic_df[hydro_economic_df['udi'] == x['demanda_mi_id']], period_factor), axis=1)
        # Rename demanda_mi_id to code
        udi_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)
        # Generate bins
        bins = pd.qcut(
            udi_simulation_df['income'], q=4, retbins=True, duplicates='drop')[1]

        return jsonify({'status': 200, 'data': {'bins': bins.tolist(), 'hydroEconomic': json.loads(udi_simulation_df[['code', 'income']].to_json(orient='records'))},  'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


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
        if x['proportion'] == 0 or hydro_economic_df.shape[0] == 0:
            return 0
        ipc = 1.141
        # Water demand income
        water_demand_income = np.interp(
            [x['proportion']], hydro_economic_df['proportion'], hydro_economic_df['cost'])[0] * ipc / period_factor

        return water_demand_income - water_cost


@hydro_economic_bp.route('/get-wetland-income', methods=['GET'])
def get_wetland_income():
    line = request.args.get('line')
    period = request.args.get('period')

    try:
        # Read planification or optimization data
        try:
            if period == 'daily':
                period_factor = 365
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_S/last_daily.csv', index_col=[0])
            elif period == 'monthlyDaily':
                period_factor = 12
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_daily.csv', index_col=[0])
            elif period == 'monthlyMonthly':
                period_factor = 12
                simulation_df = pd.read_csv(
                    current_app.config['DATA_FOLDER'] + f'/{line}/OUT/SIMUL_M/last_monthly.csv', index_col=[0])
            else:
                raise Exception('Period not supported')
        except Exception as e:
            raise Exception(f'Error reading {line} with period {period} data')
        # Filter by demand type
        humedal_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'HUMEDAL')]
        # Get simulation flow and flow max mean
        humedal_simulation_df = humedal_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Get wetland ha
        wetlands = demand_units_schema.dump(
            DemandUnitModel.get_values('wetland'))
        # Calculate income
        ipc = 1.21
        humedal_simulation_df['income'] = humedal_simulation_df.apply(
            lambda x: calculate_wetland_income(x, wetlands, ipc, period_factor), axis=1)
        # Rename demanda_mi_id to code
        humedal_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)
        # Generate bins
        bins = pd.qcut(
            humedal_simulation_df['income'], q=4, retbins=True, duplicates='drop')[1]

        return jsonify({'status': 200, 'data': {'bins': bins.tolist(), 'hydroEconomic': json.loads(humedal_simulation_df[['code', 'income']].to_json(orient='records'))},  'ok': True})

    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


def calculate_wetland_income(x, wetlands, ipc, period_factor):
    # Calculate income
    cost = 915  # € ha / year
    wetland_income = 0
    for wetland in wetlands:
        if wetland['code'] == x['demanda_mi_id']:
            wetland_income = (wetland['surface'] * cost) * ipc / period_factor

    # Water cost
    water_cost = x['flow'] * (x['tipo_agua_superficial'] * WATER_COST['tipo_agua_superficial'] + x['tipo_agua_subterranea'] * WATER_COST['tipo_agua_subterranea'] + x['tipo_agua_reutilizada']
                              * WATER_COST['tipo_agua_reutilizada'] + x['tipo_agua_trasvase'] * WATER_COST['tipo_agua_trasvase'] + x['tipo_agua_desalada'] * WATER_COST['tipo_agua_desalada'])
    if np.isnan(water_cost):
        water_cost = 0

    return wetland_income - water_cost
