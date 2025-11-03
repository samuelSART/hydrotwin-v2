from sqlalchemy import Column, String, func, text
from sqlalchemy.orm import relationship, joinedload, column_property
from geoalchemy2 import Geometry
from marshmallow import fields
import json

from app import db, ma


class ControlPointModel(db.Model):
    __tablename__ = 'control_point'

    # Document variables
    code = Column(String(), primary_key=True)
    denomination = Column(String())
    municipality = Column(String())
    province = Column(String())
    typology = Column(String())
    description = Column(String())
    water_body = Column(String())
    location = Column(Geometry())
    location_json = column_property(
        func.ST_AsGeoJSON(func.ST_Transform(location, 4326)))

    measurement_point_relation = relationship(
        "MeasurementPointModel", back_populates="control_point_relation")

    @staticmethod
    def get_values(control_points=None):
        session = db.create_scoped_session()
        if control_points:
            results = session.query(ControlPointModel).options(joinedload(
                ControlPointModel.measurement_point_relation)).where(ControlPointModel.code.in_(control_points))
        else:
            results = session.query(ControlPointModel).options(
                joinedload(ControlPointModel.measurement_point_relation)).all()
        session.close()
        return results

    def write_values(control_points=None):
        query = ''' INSERT INTO public.control_point (code, denomination, municipality, province, typology, description, location) 
                    VALUES(%(code)s, %(denomination)s, %(municipality)s, %(province)s, %(typology)s, %(description)s, ST_SetSRID(ST_MakePoint(%(x)s,%(y)s), 25830)) 
                    ON CONFLICT ON CONSTRAINT control_point_pkey 
                    DO UPDATE SET denomination = %(denomination)s, 
                                municipality = %(municipality)s, 
                                province = %(province)s, 
                                typology = %(typology)s, 
                                description = %(description)s, 
                                location = ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), 25830); '''
        if control_points:
            with db.engine.begin() as conn:
                return conn.exec_driver_sql(query, control_points)
        else:
            raise Exception("No control points specified")


class ControlPointSchema(ma.Schema):
    class Meta:
        fields = ('code', 'denomination', 'municipality', 'province', 'typology',
                  'description', 'water_body', 'location', 'measurement_point_relation')

    location = fields.Method('geometry_to_json')
    measurement_point_relation = fields.Nested('MeasurementPointSchema', exclude=(
        'control_point_relation', 'variable_relation',), many=True, data_key="measurement_points")

    def geometry_to_json(self, obj):
        return json.loads(obj.location_json)


control_point_schema = ControlPointSchema()
control_points_schema = ControlPointSchema(many=True)
