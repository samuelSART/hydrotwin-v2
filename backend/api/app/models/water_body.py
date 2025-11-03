from sqlalchemy import Column, String, func, Float
from sqlalchemy.orm import relationship, column_property
from geoalchemy2 import Geometry
from marshmallow import fields
import json


from app import db, ma


class WaterBodyModel(db.Model):
    __tablename__ = 'water_body'

    # Document variables
    code = Column(String(), primary_key=True)
    type = Column(String())
    name = Column(String())
    category = Column(String())
    geometry = Column(Geometry())
    geometry_json = column_property(
        func.ST_AsGeoJSON(func.ST_Transform(geometry, 4326)))
    generator_flow = Column(Float())

    environmental_flow_relation = relationship(
        "EnvironmentalFlowModel", back_populates="water_body_relation")
    dam_relation = relationship(
        "DamModel", back_populates="water_body_relation")

    @staticmethod
    def get_values(code=None, wb_type=None):
        session = db.create_scoped_session()
        if code:
            results = session.query(WaterBodyModel).filter(WaterBodyModel.code == code).all()
        elif wb_type:
            results = session.query(WaterBodyModel).filter(WaterBodyModel.type == wb_type).all()
        else:
            results = session.query(WaterBodyModel).all()
        session.close()
        return results

    @staticmethod
    def get_by_position(geometry):
        session = db.create_scoped_session()
        results = session.query(WaterBodyModel).filter(WaterBodyModel.geometry.intersects(str(geometry))).all()
        session.close()
        return results


class WaterBodySchema(ma.Schema):
    class Meta:
        fields = ('code', 'type', 'category',
                  'name', 'geometry', 'generator_flow')

    geometry = fields.Method('geometry_to_json')

    def geometry_to_json(self, obj):
        return json.loads(obj.geometry_json)


water_body_schema = WaterBodySchema()
water_bodies_schema = WaterBodySchema(many=True)
