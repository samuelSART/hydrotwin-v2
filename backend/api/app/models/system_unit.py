from sqlalchemy import Column, String, NUMERIC, func
from sqlalchemy.orm import column_property
from geoalchemy2 import Geometry
from marshmallow import fields
import json

from app import db, ma


class SystemUnitModel(db.Model):
    __tablename__ = 'system_unit'

    # Document variables
    zone = Column(String(), primary_key=True)
    name = Column(String())
    ha = Column(NUMERIC())
    geometry = Column(Geometry())
    geometry_json = column_property(
        func.ST_AsGeoJSON(func.ST_Transform(geometry, 4326)))

    @staticmethod
    def get_values(zone):
        session = db.create_scoped_session()
        if zone is None:
            results = session.query(SystemUnitModel).all()
        else:
            results = session.query(SystemUnitModel).filter(
                SystemUnitModel.zone == zone).all()
        session.close()
        return results


class SystemUnitSchema(ma.Schema):
    class Meta:
        fields = ('zone', 'name', 'ha', 'geometry')

    geometry = fields.Method('geometry_to_json')

    def geometry_to_json(self, obj):
        return json.loads(obj.geometry_json)


system_unit_schema = SystemUnitSchema()
system_units_schema = SystemUnitSchema(many=True)
