from sqlalchemy import Column, DateTime, String, Float
from marshmallow import fields

from app import db, ma


class SAIHModel(db.Model):
    __tablename__ = 'sensor_data'
    
    # Document variables
    timestamp = Column(DateTime(), primary_key=True)
    variable_code = Column(String(), primary_key=True)
    value = Column(Float())
    
    @staticmethod
    def get_values(variable_codes, start_date, end_date):
        try:
            if start_date != None and end_date != None:
                return SAIHModel.query.filter(SAIHModel.variable_code.in_(variable_codes), SAIHModel.timestamp.between(start_date, end_date))
            elif start_date != None and end_date == None:
                return SAIHModel.query.filter(SAIHModel.variable_code.in_(variable_codes), SAIHModel.timestamp >= start_date)
            elif start_date == None and end_date != None:
                return SAIHModel.query.filter(SAIHModel.variable_code.in_(variable_codes), SAIHModel.timestamp <= end_date)
            else:
                return SAIHModel.query.filter(SAIHModel.variable_code.in_(variable_codes))
        except Exception as e:
            raise e
    
    @staticmethod
    def get_all_values(start_date, end_date):
        try:
            if start_date != None and end_date != None:
                return SAIHModel.query.filter(SAIHModel.timestamp.between(start_date, end_date))
            elif start_date != None and end_date == None:
                return SAIHModel.query.filter(SAIHModel.timestamp >= start_date)
            elif start_date == None and end_date != None:
                return SAIHModel.query.filter(SAIHModel.timestamp <= end_date)
        except Exception as e:
            raise e


class SAIHSchema(ma.Schema):
    timestamp = fields.DateTime()
    variable_code = fields.Str()
    value = fields.Float()


saih_schema = SAIHSchema()
saihs_schema = SAIHSchema(many=True)
