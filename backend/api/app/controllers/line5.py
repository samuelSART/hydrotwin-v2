import os
import json
import psutil
import logging
from multiprocessing import Process
from flask import Blueprint, request, jsonify, current_app, send_file

from app.utils import optimizer, planner


line5_bp = Blueprint('line5', __name__)

DATA_FOLDER = current_app.config['DATA_FOLDER']
PLAN_FOLDER = DATA_FOLDER + '/L4/OUT/'
OPTIMIZER_FOLDER = DATA_FOLDER + '/L5/OUT/'
PIDFILE = optimizer.PIDFILE


@line5_bp.route('/generate-optimized-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    scenario = data.get(
        'scenario') if data is not None and 'scenario' in data else None
    superficial = float(scenario.get(
        'superficial')) / 100 if scenario is not None and 'superficial' in scenario else 1.0
    subterranea = float(scenario.get(
        'subterranea')) / 100 if scenario is not None and 'subterranea' in scenario else 1.0
    reutilizada = float(scenario.get(
        'reutilizada')) / 100 if scenario is not None and 'reutilizada' in scenario else 1.0
    trasvase = float(scenario.get(
        'trasvase')) / 100 if scenario is not None and 'trasvase' in scenario else 1.0
    desalada = float(scenario.get(
        'desalada')) / 100 if scenario is not None and 'desalada' in scenario else 1.0
    waterDeficit = float(scenario.get(
        'waterDeficit')) / 100 if scenario is not None and 'waterDeficit' in scenario else 1.0
    CO2impact = float(scenario.get(
        'CO2impact')) / 100 if scenario is not None and 'CO2impact' in scenario else 1.0
    economicImpact = float(scenario.get(
        'economicImpact')) / 100 if scenario is not None and 'economicImpact' in scenario else 1.0
    data = request.args
    monthly = (request.args.get(
        'monthly') == "true") if data is not None and 'monthly' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    
    if os.path.isfile(PIDFILE):
        PID = int(open(PIDFILE).readline())
        if psutil.pid_exists(PID):
            return jsonify({'status': 202, 'title': 'Simulation already running', 
                'detail': 'Simulation is already running. Please wait to finish to start a new one.', 'ok': False}), 202
        else:
            os.unlink(PIDFILE)
            logging.warning('Last simulation may have terminated abnormally!')
            # return jsonify({'status': 503, 'title': 'Simulation terminated abnormally', 
            #     'detail': 'Last simulation may have terminated abnormally, please retry.', 'ok': False}), 503
    
    try:
        process_name = 'optimizer-monthly' if monthly else 'optimizer-daily'
        optimizer_proc = Process(name=process_name, target=optimizer.generate_optimzied_plan, 
                args=(superficial, subterranea, reutilizada, trasvase, desalada, waterDeficit, CO2impact, economicImpact, monthly, daily))
        optimizer_proc.start()
        return jsonify({'status': 200, 'data': optimizer_proc.pid, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line5_bp.route('/check-optimized-plan-generated', methods=['GET'])
def check_optimized_plan_generated():
    data = request.args
    PID = int(request.args.get('id')) if data is not None and 'id' in data else False
    try:
        if PID and psutil.pid_exists(PID):
            proc = psutil.Process(PID)
            if proc.status() == 'running':
                return jsonify({'status': 201, 'title': 'Still not ready', 
                    'detail': 'Simulation is not finished yet. Please try again in a moment.', 'ok': True}), 201
            elif proc.status() == 'zombie':
                proc.kill()
        
        if os.path.isfile(PIDFILE): os.unlink(PIDFILE)
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line5_bp.route('/optimized-plan-config-data', methods=['GET'])
def get_optimized_plan_config():
    data = request.args
    monthly = (request.args.get(
        'monthly') == "true") if data is not None and 'monthly' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    if monthly:
        if daily:
            file = OPTIMIZER_FOLDER+"/SIMUL_M/last_daily_optimized_plan_data.json"
        else:
            file = OPTIMIZER_FOLDER+"/SIMUL_M/last_monthly_optimized_plan_data.json"
    else:
        file = OPTIMIZER_FOLDER+"/SIMUL_S/last_daily_optimized_plan_data.json"
    
    if not os.path.isfile(file):
        # return jsonify({'status': 500, 'title': 'Error', 'detail': "No planification generated", 'ok': False}), 500
        return jsonify({'status': 202, 'title': 'Warning', 'detail': "No planification generated", 'ok': False}), 202
    
    try:
        f = open(file)
        data = json.load(f)
        f.close()
        return jsonify({'status': 200, 'data': data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line5_bp.route('/table-data', methods=['GET'])
def table_data():
    data = request.args
    type = request.args.get(
        'type') if data is not None and 'type' in data else None
    monthly = (request.args.get(
        'monthly') == "true") if data is not None and 'monthly' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    
    if monthly:
        if daily:
            file = OPTIMIZER_FOLDER+"/SIMUL_M/last_daily.csv"
        else:
            file = OPTIMIZER_FOLDER+"/SIMUL_M/last_monthly.csv"
    else:
        file = OPTIMIZER_FOLDER+"SIMUL_S/last_daily.csv"
    
    if not os.path.isfile(file):
        # return jsonify({'status': 500, 'title': 'Error', 'detail': "No planification generated", 'ok': False}), 500
        return jsonify({'status': 202, 'title': 'Warning', 'detail': "No planification generated", 'ok': False}), 202
    
    try:
        if type is not None:
            table_data = planner.read_type_table(file, type, monthly)
        else:
            table_data = planner.read_table(file, monthly)
        return jsonify({'status': 200, 'data': table_data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line5_bp.route('/plot-data', methods=['GET'])
def plot_data():
    data = request.args
    id = request.args.get('id') if data is not None and 'id' in data else None
    type = request.args.get(
        'type') if data is not None and 'type' in data else None
    monthly = (request.args.get(
        'monthly') == "true") if data is not None and 'monthly' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    
    if monthly:
        if daily:
            file = OPTIMIZER_FOLDER+"/SIMUL_M/last_daily.csv"
        else:
            file = OPTIMIZER_FOLDER+"/SIMUL_M/last_monthly.csv"
    else:
        file = OPTIMIZER_FOLDER+"SIMUL_S/last_daily.csv"
    
    if not os.path.isfile(file):
        # return jsonify({'status': 500, 'title': 'Error', 'detail': "No planification generated", 'ok': False}), 500
        return jsonify({'status': 202, 'title': 'Warning', 'detail': "No planification generated", 'ok': False}), 202
    
    if monthly:
        if daily:
            old_plan_file = PLAN_FOLDER+"/SIMUL_M/last_daily.csv"
        else:
            old_plan_file = PLAN_FOLDER+"/SIMUL_M/last_monthly.csv"
    else:
        old_plan_file = PLAN_FOLDER+"/SIMUL_S/last_daily.csv"
    
    if not os.path.isfile(old_plan_file):
        old_plan_file = None
    
    try:
        if id is not None:
            plot_data = optimizer.read_unit_plot(
                file, old_plan_file, id, monthly)
        elif type is not None:
            plot_data = optimizer.read_type_plot(
                file, old_plan_file, type, monthly)
        else:
            plot_data = optimizer.read_plot(file, old_plan_file, monthly)
        return jsonify({'status': 200, 'data': plot_data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line5_bp.route('/download-plan', methods=['GET'])
def download_plan():
    data = request.args
    long = (request.args.get(
        'long') == "true") if data is not None and 'long' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    try:
        if long:
            if daily:
                file = OPTIMIZER_FOLDER+"/SIMUL_M/last_daily.csv"
            else:
                file = OPTIMIZER_FOLDER+"/SIMUL_M/last_monthly.csv"
        else:
            file = OPTIMIZER_FOLDER+"SIMUL_S/last_daily.csv"
        if not os.path.isfile(file):
            return jsonify({'status': 204, 'data': [], 'ok': True}), 204
        return send_file(file, as_attachment=True, attachment_filename='plan.csv'), 200
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
