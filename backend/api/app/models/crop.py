from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from marshmallow import fields

from app import db, ma


class CropModel(db.Model):
    __tablename__ = 'crop'

    demand_unit_code = Column(String(), ForeignKey(
        "demand_unit.code"), primary_key=True)
    cereales_invierno = Column(Integer())
    arroz = Column(Integer())
    cereales_primavera = Column(Integer())
    tuberculos = Column(Integer())
    horticolas_protegido = Column(Integer())
    horticolas_libre = Column(Integer())
    citricos = Column(Integer())
    frutales_fruto_carnoso = Column(Integer())
    almendro = Column(Integer())
    vinedo_vino = Column(Integer())
    vinedo_mesa = Column(Integer())
    olivar = Column(Integer())
    total = Column(Integer())

    demand_unit_relation = relationship(
        "DemandUnitModel", back_populates="crop_relation")

    @staticmethod
    def get_crops(demand_unit_code=None):
        session = db.create_scoped_session()
        if(demand_unit_code is None):
            results = session.query(CropModel).all()
        else:
            results = session.query(CropModel).filter(
                CropModel.demand_unit_code == demand_unit_code).all()
        session.close()
        return results


class CropSchema(ma.Schema):
    demand_unit_code = fields.String()
    cereales_invierno = fields.Integer()
    arroz = fields.Integer()
    cereales_primavera = fields.Integer()
    tuberculos = fields.Integer()
    horticolas_protegido = fields.Integer()
    horticolas_libre = fields.Integer()
    citricos = fields.Integer()
    frutales_fruto_carnoso = fields.Integer()
    almendro = fields.Integer()
    vinedo_vino = fields.Integer()
    vinedo_mesa = fields.Integer()
    olivar = fields.Integer()
    total = fields.Integer()


crop_schema = CropSchema()
crops_schema = CropSchema(many=True)
