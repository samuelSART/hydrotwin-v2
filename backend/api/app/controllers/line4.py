import os
import json
import psutil
import logging
from multiprocessing import Process
from flask import Blueprint, request, jsonify, current_app, send_file

from app.utils import planner
from app.utils.compute_rec import getResources
from app.utils.compute_rec_dem_anual import getDemandResources


line4_bp = Blueprint('line4', __name__)


DATA_FOLDER = current_app.config['DATA_FOLDER']
PLAN_FOLDER = DATA_FOLDER + '/L4/OUT/'
PIDFILE = planner.PIDFILE


@line4_bp.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    scenario = data.get(
        'scenario') if data is not None and 'scenario' in data else None
    superficial = float(scenario.get(
        'superficial') / 100) if scenario is not None and 'superficial' in scenario else 1.0
    subterranea = float(scenario.get(
        'subterranea') / 100) if scenario is not None and 'subterranea' in scenario else 1.0
    reutilizada = float(scenario.get(
        'reutilizada') / 100) if scenario is not None and 'reutilizada' in scenario else 1.0
    trasvase = float(scenario.get(
        'trasvase') / 100) if scenario is not None and 'trasvase' in scenario else 1.0
    desalada = float(scenario.get(
        'desalada') / 100) if scenario is not None and 'desalada' in scenario else 1.0
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
        process_name = 'planner-monthly' if monthly else 'planner-daily'
        planner_proc = Process(name=process_name, target=planner.generate_plan,
                               args=(superficial, subterranea, reutilizada, trasvase, desalada, monthly, daily))
        planner_proc.start()
        return jsonify({'status': 200, 'data': planner_proc.pid, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line4_bp.route('/check-plan-generated', methods=['GET'])
def check_plan_generated():
    data = request.args
    PID = int(request.args.get('id')
              ) if data is not None and 'id' in data else False
    try:
        if PID and psutil.pid_exists(PID):
            proc = psutil.Process(PID)
            if proc.status() == 'running':
                return jsonify({'status': 201, 'title': 'Still not ready',
                                'detail': 'Simulation is not finished yet. Please try again in a moment.', 'ok': True}), 201
            elif proc.status() == 'zombie':
                proc.kill()

        if os.path.isfile(PIDFILE):
            os.unlink(PIDFILE)
        return jsonify({'status': 200, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line4_bp.route('/plan-config-data', methods=['GET'])
def get_plan_config():
    data = request.args
    monthly = (request.args.get(
        'monthly') == "true") if data is not None and 'monthly' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    if monthly:
        if daily:
            file = PLAN_FOLDER+"/SIMUL_M/last_daily_plan_data.json"
        else:
            file = PLAN_FOLDER+"/SIMUL_M/last_monthly_plan_data.json"
    else:
        file = PLAN_FOLDER+"/SIMUL_S/last_daily_plan_data.json"

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


@line4_bp.route('/get-resources', methods=['GET'])
def get_resources():
    try:
        data = getResources()
        return jsonify({'status': 200, 'data': data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line4_bp.route('/get-demand-resources', methods=['GET'])
def get_demand_resources():
    try:
        data = getDemandResources()
        return jsonify({'status': 200, 'data': data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line4_bp.route('/table-data', methods=['GET'])
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
            file = PLAN_FOLDER+"/SIMUL_M/last_daily.csv"
        else:
            file = PLAN_FOLDER+"/SIMUL_M/last_monthly.csv"
    else:
        file = PLAN_FOLDER+"/SIMUL_S/last_daily.csv"

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


@line4_bp.route('/plot-data', methods=['GET'])
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
            file = PLAN_FOLDER+"/SIMUL_M/last_daily.csv"
        else:
            file = PLAN_FOLDER+"/SIMUL_M/last_monthly.csv"
    else:
        file = PLAN_FOLDER+"/SIMUL_S/last_daily.csv"

    if not os.path.isfile(file):
        # return jsonify({'status': 500, 'title': 'Error', 'detail': "No planification generated", 'ok': False}), 500
        return jsonify({'status': 202, 'title': 'Warning', 'detail': "No planification generated", 'ok': False}), 202

    try:
        if id is not None:
            plot_data = planner.read_unit_plot(file, id, monthly)
        elif type is not None:
            plot_data = planner.read_type_plot(file, type, monthly)
        else:
            plot_data = planner.read_plot(file, monthly)
        return jsonify({'status': 200, 'data': plot_data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500


@line4_bp.route('/download-plan', methods=['GET'])
def download_plan():
    data = request.args
    long = (request.args.get(
        'long') == "true") if data is not None and 'long' in data else False
    daily = (request.args.get(
        'daily') == "true") if data is not None and 'daily' in data else False
    try:
        if long:
            if daily:
                file = PLAN_FOLDER+"/SIMUL_M/last_daily.csv"
            else:
                file = PLAN_FOLDER+"/SIMUL_M/last_monthly.csv"
        else:
            file = PLAN_FOLDER+"/SIMUL_S/last_daily.csv"

        if not os.path.isfile(file):
            return jsonify({'status': 204, 'data': [], 'ok': True}), 204
        return send_file(file, as_attachment=True, attachment_filename='plan.csv'), 200
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'detail': str(e), 'ok': False}), 500
