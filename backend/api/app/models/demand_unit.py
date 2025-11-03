from sqlalchemy import Column, String, Float, func
from sqlalchemy.orm import relationship, column_property
from geoalchemy2 import Geometry
from marshmallow import fields
import json

from app import db, ma


class DemandUnitModel(db.Model):
    __tablename__ = 'demand_unit'

    # Document variables
    code = Column(String(), primary_key=True)
    type = Column(String())
    name = Column(String())
    surface = Column(Float())
    geometry = Column(Geometry())
    geometry_json = column_property(
        func.ST_AsGeoJSON(func.ST_Transform(geometry, 4326)))

    crop_relation = relationship(
        "CropModel", back_populates="demand_unit_relation")

    @staticmethod
    def get_values(type=None, code=None):
        session = db.create_scoped_session()
        if type != None and code != None:
            results = session.query(DemandUnitModel).filter(
                DemandUnitModel.type == type and DemandUnitModel.code == code).all()
        elif type != None and code == None:
            results = session.query(DemandUnitModel).filter(
                DemandUnitModel.type == type).all()
        elif type == None and code != None:
            results = session.query(DemandUnitModel).filter(
                DemandUnitModel.code == code).all()
        else:
            results = session.query(DemandUnitModel).all()
        session.close()
        return results

    @staticmethod
    def get_by_position(geometry):
        session = db.create_scoped_session()
        results = session.query(DemandUnitModel).filter(
            DemandUnitModel.geometry.intersects(str(geometry))).all()
        session.close()
        return results


class DemandUnitSchema(ma.Schema):
    class Meta:
        fields = ('code', 'type', 'name', 'surface', 'geometry')

    geometry = fields.Method('geometry_to_json')

    def geometry_to_json(self, obj):
        return json.loads(obj.geometry_json)


demand_unit_schema = DemandUnitSchema()
demand_units_schema = DemandUnitSchema(many=True)
