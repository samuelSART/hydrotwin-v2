from sqlalchemy import Column, String, ForeignKey, func
from sqlalchemy.orm import relationship, joinedload, column_property
from geoalchemy2 import Geometry
from marshmallow import fields
import json


from app import db, ma


class MeasurementPointModel(db.Model):
    __tablename__ = 'measurement_point'

    # Document variables
    code = Column(String(), primary_key=True)
    denomination = Column(String())
    description = Column(String())
    typology = Column(String())
    location = Column(Geometry())
    location_json = column_property(
        func.ST_AsGeoJSON(func.ST_Transform(location, 4326)))
    control_point = Column(String(), ForeignKey("control_point.code"))

    control_point_relation = relationship(
        "ControlPointModel", back_populates="measurement_point_relation")
    variable_relation = relationship(
        "VariableModel", back_populates="measurement_point_relation")

    @staticmethod
    def get_values(measurement_points=None, typology=None):
        session = db.create_scoped_session()
        if measurement_points:
            results = session.query(MeasurementPointModel).options(joinedload(MeasurementPointModel.control_point_relation),
                                                                   joinedload(MeasurementPointModel.variable_relation)).where(MeasurementPointModel.code.in_(measurement_points))
        elif typology:
            results = session.query(MeasurementPointModel).options(joinedload(MeasurementPointModel.control_point_relation),
                                                                   joinedload(MeasurementPointModel.variable_relation)).where(MeasurementPointModel.typology.in_(typology))
        else:
            results = session.query(MeasurementPointModel).options(joinedload(MeasurementPointModel.control_point_relation),
                                                                   joinedload(MeasurementPointModel.variable_relation)).all()
        session.close()
        return results

    def write_values(measurement_points=None):
        query = ''' INSERT INTO public.measurement_point (code, control_point, denomination, typology, description, location) 
                    VALUES(%(code)s, %(control_point)s, %(denomination)s, %(typology)s, %(description)s, ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), 25830)) 
                    ON CONFLICT ON CONSTRAINT measurement_point_pkey
                    DO UPDATE SET denomination = %(denomination)s, 
                                control_point = %(control_point)s,
                                typology = %(typology)s, 
                                description = %(description)s,
                                location = ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), 25830); '''
        if measurement_points:
            with db.engine.begin() as conn:
                conn.exec_driver_sql(query, measurement_points)
        else:
            raise Exception("No measurement points specified")

    @staticmethod
    def get_piezometers():
        session = db.create_scoped_session()
        results = session.query(MeasurementPointModel).options(joinedload(MeasurementPointModel.control_point_relation),
                                                               joinedload(MeasurementPointModel.variable_relation)).where(MeasurementPointModel.denomination.like('%Piezo%'))
        session.close()
        return results


class MeasurementPointSchema(ma.Schema):
    class Meta:
        fields = ('code', 'denomination', 'typology', 'description',
                  'location', 'control_point_relation', 'variable_relation')

    location = fields.Method('geometry_to_json')
    control_point_relation = fields.Nested(
        'ControlPointSchema', exclude=("measurement_point_relation",), many=False, data_key="control_point")
    variable_relation = fields.Nested('VariableSchema', exclude=(
        "measurement_point_relation",), many=True, data_key="variables")

    def geometry_to_json(self, obj):
        return json.loads(obj.location_json)


measurement_point_schema = MeasurementPointSchema()
measurement_points_schema = MeasurementPointSchema(many=True)
