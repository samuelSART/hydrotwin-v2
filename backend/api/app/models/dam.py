from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from marshmallow import fields
import json

from app import db, ma


class DamModel(db.Model):
    __tablename__ = 'dam'

    # Document variables
    water_body = Column(String(), ForeignKey(
        "water_body.code"), primary_key=True)
    variable = Column(String(), ForeignKey("variable.code"), primary_key=True)
    typology = Column(String(), ForeignKey(
        "variable.typology"), primary_key=True)
    max_oct_dic = Column(Float())
    max_ene_mar = Column(Float())
    max_abr_jun = Column(Float())
    max_jul_sep = Column(Float())
    min_oct_dic = Column(Float())
    min_ene_mar = Column(Float())
    min_abr_jun = Column(Float())
    min_jul_sep = Column(Float())

    water_body_relation = relationship(
        "WaterBodyModel", back_populates="dam_relation")
    variable_code_relation = relationship(
        "VariableModel", foreign_keys=[variable])
    variable_typology_relation = relationship(
        "VariableModel", foreign_keys=[typology])

    @staticmethod
    def get_dams_variables():
        session = db.create_scoped_session()
        results = session.query(DamModel).options(
            joinedload(DamModel.water_body_relation)).all()
        session.close()
        return results

    @staticmethod
    def get_dam_variables(dam_code):
        session = db.create_scoped_session()
        results = session.query(DamModel.variable, DamModel.typology).filter(
            DamModel.water_body == dam_code).all()
        session.close()
        return results

    @staticmethod
    def get_dam_by_variable(variable):
        session = db.create_scoped_session()
        results = session.query(DamModel).options(joinedload(
            DamModel.water_body_relation)).filter(DamModel.variable == variable).all()
        session.close()
        return results

    @staticmethod
    def get_dams_variable_typology(variable_typology):
        session = db.create_scoped_session()
        results = session.query(DamModel).options(joinedload(
            DamModel.water_body_relation)).filter(DamModel.typology == variable_typology).all()
        session.close()
        return results


class DamSchema(ma.Schema):
    class Meta:
        fields = ('water_body_relation', 'variable', 'typology', 'max_oct_dic', 'max_ene_mar',
                  'max_abr_jun', 'max_jul_sep', 'min_oct_dic', 'min_ene_mar', 'min_abr_jun', 'min_jul_sep')

    water_body_relation = fields.Nested('WaterBodySchema', exclude=(
        "type", "category"), data_key="water_body")

    def geometry_to_json(self, obj):
        return json.loads(obj.location_json)


dam_schema = DamSchema()
dams_schema = DamSchema(many=True)
