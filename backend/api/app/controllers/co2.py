from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import json

from ..models.crop import CropModel, crops_schema
from ..utils.co2 import calculate_agriculture_emissions, calculate_urban_emissions, calculate_industry_emissions, calculate_golf_emissions, calculate_wetland_emissions

co2_bp = Blueprint('co2', __name__)


@co2_bp.route('/get-agriculture-emissions', methods=['GET'])
def get_agriculture_emissions():
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

        # Get agriculture demands crop types
        demands_crops = crops_schema.dump(CropModel.get_crops())
        # Filter by demand type
        uda_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'UDA')]
        # Get simulation flow and water demand distribution
        uda_simulation_df = uda_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        uda_simulation_df.fillna(
            uda_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Rename demanda_mi_id to uda
        uda_simulation_df.rename(
            columns={'demanda_mi_id': 'demand_unit_code'}, inplace=True)
        # Calculate agriculture emissions
        emissions = calculate_agriculture_emissions(
            demands_crops, uda_simulation_df, period_factor)

        df = pd.DataFrame(emissions, columns=['code', 'total'])
        bins = pd.qcut(df['total'].drop_duplicates(), q=4, retbins=True)[1]

        return jsonify({'status': 200, 'data': {"emissions": emissions, "bins": bins.tolist()}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ co2_bp.route('/get-urban-emissions', methods=['GET'])
def get_urban_emissions():
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
        # Get simulation flow and water demand distribution
        udu_simulation_df = udu_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        udu_simulation_df.fillna(
            udu_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Rename demanda_mi_id to uda
        udu_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)

        # Calculate urban emissions
        emissions_df = calculate_urban_emissions(udu_simulation_df)
        # Calculate bins with total emissions
        bins = pd.qcut(
            emissions_df['total'].drop_duplicates(), q=4, retbins=True)[1]

        return jsonify({'status': 200, 'data': {"emissions": json.loads(emissions_df[['code', 'total', 'demand', 'water']].to_json(orient='records')), "bins": bins.tolist()}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ co2_bp.route('/get-industry-emissions', methods=['GET'])
def get_industry_emissions():
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
        udi_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'UDI')]
        # Get simulation flow and water demand distribution
        udi_simulation_df = udi_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        udi_simulation_df.fillna(
            udi_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Rename demanda_mi_id to uda
        udi_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)

        # Calculate industry emissions
        emissions_df = calculate_industry_emissions(udi_simulation_df)
        # Calculate bins with total emissions
        bins = pd.qcut(
            emissions_df['total'].drop_duplicates(), q=4, retbins=True)[1]

        return jsonify({'status': 200, 'data': {"emissions": json.loads(emissions_df[['code', 'total', 'demand', 'water']].to_json(orient='records')), "bins": bins.tolist()}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ co2_bp.route('/get-golf-emissions', methods=['GET'])
def get_golf_emissions():
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
        # Get simulation flow and water demand distribution
        udrg_simulation_df = udrg_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        udrg_simulation_df.fillna(
            udrg_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Rename demanda_mi_id to uda
        udrg_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)

        # Calculate golf emissions
        emissions_df = calculate_golf_emissions(udrg_simulation_df)
        # Calculate bins with total emissions
        bins = pd.qcut(
            emissions_df['total'].drop_duplicates(), q=4, retbins=True)[1]

        return jsonify({'status': 200, 'data': {"emissions": json.loads(emissions_df[['code', 'total', 'demand', 'water']].to_json(orient='records')), "bins": bins.tolist()}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@ co2_bp.route('/get-wetland-emissions', methods=['GET'])
def get_wetland_emissions():
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
        wetland_simulation_df = simulation_df[simulation_df['demanda_mi_id'].str.contains(
            'HUMEDAL')]
        # Get simulation flow and water demand distribution
        wetland_simulation_df = wetland_simulation_df.groupby(
            ['demanda_mi_id'], as_index=False)[['flow', 'init_max_flow', 'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].mean()
        # Fill NaN values with 0
        wetland_simulation_df.fillna(
            wetland_simulation_df[['tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada', 'tipo_agua_trasvase', 'tipo_agua_desalada']].fillna(0), inplace=True)
        # Rename demanda_mi_id to uda
        wetland_simulation_df.rename(
            columns={'demanda_mi_id': 'code'}, inplace=True)

        # Calculate wetlands emissions
        emissions_df = calculate_wetland_emissions(wetland_simulation_df)
        # Calculate bins with total emissions
        bins = pd.qcut(
            emissions_df['total'].drop_duplicates(), q=4, retbins=True)[1]

        return jsonify({'status': 200, 'data': {"emissions": json.loads(emissions_df[['code', 'total', 'demand', 'water']].to_json(orient='records')), "bins": bins.tolist()}, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
