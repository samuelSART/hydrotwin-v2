from datetime import datetime
from sqlalchemy import Column, INTEGER, NVARCHAR, NUMERIC, DATETIME, String, CHAR, func, and_
from sqlalchemy.orm import column_property
# from geoalchemy2 import Geometry # Commented out as it's not currrently neccesary
from app import db, ma
from marshmallow import fields


class PiezometerValue(db.Model):

    __bind_key__ = 'PIEZOMETRY_DB'
    __tablename__ = 'VistaSeriesPiezometria'
    __table_args__ = {'schema': 'SDEW'}

    # Document variables
    COD_CHS = Column(String(), primary_key=True)
    FECHA = Column(DATETIME(), primary_key=True)
    SITUACION = Column(String())
    PNP = Column(NUMERIC())
    PROYECTO = Column(String())
    SUIN = Column(NVARCHAR(10))
    DUB = Column(String())
    TDB = Column(String())
    Fecha_Alta = Column(DATETIME())
    instaladoSN = Column(CHAR(1))
    tuboGuiaSN = Column(NVARCHAR(200))
    SITUACION2 = Column(String())
    ZTOTAL = Column(NUMERIC())
    CMSNM = Column(NUMERIC())
    codEstimacion = Column(INTEGER())
    _time = column_property('')

    @staticmethod
    def get_latest_value(codes):
        session = db.create_scoped_session()
        subq = session.query(
            PiezometerValue.COD_CHS,
            func.max(PiezometerValue.FECHA).label('maxdate')
        ).group_by(PiezometerValue.COD_CHS).subquery('t2')

        results = session.query(PiezometerValue).\
            filter(PiezometerValue.COD_CHS.in_(codes)).\
            join(
                subq,
                and_(
                    PiezometerValue.COD_CHS == subq.c.COD_CHS,
                    PiezometerValue.FECHA == subq.c.maxdate
                )
        ).order_by(PiezometerValue.FECHA.desc())
        session.close()
        return results

    @staticmethod
    def get_range_values(codes, start_date, end_date):
        return PiezometerValue.query.filter(PiezometerValue.COD_CHS.in_(codes))\
            .filter(PiezometerValue.FECHA.between(start_date, end_date))\
            .order_by(PiezometerValue.COD_CHS.desc(), PiezometerValue.FECHA.desc())

    @staticmethod
    def get_first_value(codes):
        session = db.create_scoped_session()
        subq = session.query(
            PiezometerValue.COD_CHS,
            func.min(PiezometerValue.FECHA).label('mindate')
        ).group_by(PiezometerValue.COD_CHS).subquery('t2')

        results = session.query(PiezometerValue).\
            filter(PiezometerValue.COD_CHS.in_(codes)).\
            join(
                subq,
                and_(
                    PiezometerValue.COD_CHS == subq.c.COD_CHS,
                    PiezometerValue.FECHA == subq.c.mindate
                )
        ).order_by(PiezometerValue.FECHA.asc())
        session.close()
        return results


class PiezometryValueSchema(ma.Schema):
    class Meta:
        strict = True

    COD_CHS = fields.String(data_key="variableCode")
    PNP = fields.Number(data_key="_value")
    FECHA = fields.String(data_key="_iso_time")
    _time = fields.Method('datetime_to_timestamp')

    def datetime_to_timestamp(self, obj):
        date = datetime.strptime(str(obj.FECHA), '%Y-%m-%d %H:%M:%S')
        return int(date.timestamp() * 1000)


piezometry_value_schema = PiezometryValueSchema()
piezometry_values_schema = PiezometryValueSchema(many=True)
