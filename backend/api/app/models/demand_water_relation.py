from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app import db


class DemandWaterRelation(db.Model):
    __tablename__ = 'demand_water_relation'
    
    # Document variables
    demand_unit = Column(String(), ForeignKey('demand_unit.code'), primary_key=True)
    water_body = Column(String(), ForeignKey('water_body.code'), primary_key=True)
    water_bodies = relationship("WaterBodyModel", back_populates="demand_units")
    demand_units = relationship("DemandUnitModel", back_populates="water_bodies")