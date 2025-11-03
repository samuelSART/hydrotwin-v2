from sqlalchemy import Boolean, Column, SmallInteger, String, Float, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from marshmallow import fields
import json


from app import db, ma


class EnvironmentalFlowModel(db.Model):
    __tablename__ = 'environmental_flow'

    # Document variables
    variable = Column(String(), ForeignKey("variable.code"), primary_key=True)
    typology = Column(String(), ForeignKey(
        "variable.typology"), primary_key=True)
    water_body = Column(String(), ForeignKey(
        "water_body.code"), primary_key=True)
    oct_dic = Column(Float())
    ene_mar = Column(Float())
    abr_jun = Column(Float())
    jul_sep = Column(Float())
    oct_dic_seq = Column(Float())
    ene_mar_seq = Column(Float())
    abr_jun_seq = Column(Float())
    jul_sep_seq = Column(Float())
    masa_estrategica = Column(Boolean())
    sistema = Column(SmallInteger())

    variable_code_relation = relationship(
        "VariableModel", foreign_keys=[variable])
    variable_typology_relation = relationship(
        "VariableModel", foreign_keys=[typology])
    water_body_relation = relationship(
        "WaterBodyModel", back_populates="environmental_flow_relation")

    @staticmethod
    def get_water_bodies():
        session = db.create_scoped_session()
        results = session.query(EnvironmentalFlowModel).options(
            joinedload(EnvironmentalFlowModel.water_body_relation)).all()
        session.close()
        return results


class EnvironmentalFlowSchema(ma.Schema):
    class Meta:
        fields = ('variable', 'typology', 'water_body_relation', 'masa_estrategica', 'sistema',
                  'oct_dic', 'ene_mar', 'abr_jun', 'jul_sep',
                  'oct_dic_seq', 'ene_mar_seq', 'abr_jun_seq', 'jul_sep_seq')

    water_body_relation = fields.Nested(
        'WaterBodySchema', exclude=("type", "category"), data_key="water_body")

    def geometry_to_json(self, obj):
        return json.loads(obj.location_json)


environmental_flow_schema = EnvironmentalFlowSchema()
environmental_flows_schema = EnvironmentalFlowSchema(many=True)
