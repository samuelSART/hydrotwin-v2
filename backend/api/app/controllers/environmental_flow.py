from flask import Blueprint, jsonify

from ..models.environmental_flow import EnvironmentalFlowModel, environmental_flows_schema

environmental_flow_bp = Blueprint('environmental-flow', __name__)


@environmental_flow_bp.route('/get-water-bodies', methods=['GET'])
def get_water_bodies():
    water_bodies = environmental_flows_schema.dump(
        EnvironmentalFlowModel.get_water_bodies())
    return jsonify({'status': 200, 'data': water_bodies, 'ok': True})
