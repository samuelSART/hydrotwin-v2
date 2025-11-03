from sqlalchemy import Column, String, ForeignKey, text, and_
from sqlalchemy.orm import relationship, joinedload
from marshmallow import fields

from app import db, ma


class VariableModel(db.Model):
    __tablename__ = 'variable'

    # Document variables
    code = Column(String(), primary_key=True)
    typology = Column(String(), primary_key=True)
    description = Column(String())
    measurement_point = Column(String(), ForeignKey("measurement_point.code"))

    measurement_point_relation = relationship(
        "MeasurementPointModel", back_populates="variable_relation")

    @staticmethod
    def get_values(variables=None, measurement_points=None, typology=None):
        if variables:
            return VariableModel.query.options(joinedload(VariableModel.measurement_point_relation)).where(VariableModel.code.in_(variables))
        elif measurement_points and typology:
            return VariableModel.query.filter(and_(VariableModel.measurement_point.in_(measurement_points), VariableModel.typology.in_(typology)))
        elif measurement_points:
            return VariableModel.query.filter(VariableModel.measurement_point.in_(measurement_points))
        elif typology:
            return VariableModel.query.options(joinedload(VariableModel.measurement_point_relation)).where(VariableModel.typology.in_(typology))
        else:
            return VariableModel.query.options(joinedload(VariableModel.measurement_point_relation)).all()

    def write_values(variables=None):
        query = ''' INSERT INTO public.variable (code, measurement_point, typology, description) 
                    VALUES(%(code)s, %(measurement_point)s, %(typology)s, %(description)s) 
                    ON CONFLICT ON CONSTRAINT variable_pkey
                    DO UPDATE SET measurement_point = %(measurement_point)s, 
                                    typology = %(typology)s, 
                                    description = %(description)s; '''
        if variables:
            with db.engine.begin() as conn:
                conn.exec_driver_sql(query, variables)
        else:
            raise Exception("No variables specified")

    @staticmethod
    def get_typology(code):
        return VariableModel.query.filter(VariableModel.code == code).first().typology


class VariableSchema(ma.Schema):
    class Meta:
        fields = ('code', 'typology', 'description',
                  'measurement_point_relation')

    measurement_point_relation = fields.Nested('MeasurementPointSchema', exclude=(
        'control_point_relation', 'variable_relation',), many=False, data_key="measurement_point")


variable_schema = VariableSchema()
variables_schema = VariableSchema(many=True)
