import logging
from sqlalchemy import Column, DATE, FLOAT, NVARCHAR
from app import db, ma

class DroughtIndices(db.Model):
    __bind_key__ = 'DROUGHTINDICES_DB'
    __tablename__ = 'INDICES_ESTADO_REV2018'
    __table_args__ = {'schema': 'SEQUIAS'}

    # Document variables
    FECHA = Column(DATE(), primary_key=True)
    CUENCA = Column(FLOAT())
    TRASVASE = Column(FLOAT())
    GLOBAL = Column(FLOAT())
    UTE_I_Situacion = Column(NVARCHAR(30))
    UTE_I_Escenario = Column(NVARCHAR(30))
    UTE_II_Cabecera = Column(FLOAT())
    UTE_II_Situacion = Column(NVARCHAR(30))
    UTE_II_Escenario = Column(NVARCHAR(30))
    UTE_III_RiosMI = Column(FLOAT())
    UTE_III_Situacion = Column(NVARCHAR(30))
    UTE_III_Escenario = Column(NVARCHAR(30))
    UTE_IV_RiosMD = Column(FLOAT())
    UTE_IV_Situacion = Column(NVARCHAR(30))
    UTE_IV_Escenario = Column(NVARCHAR(30))
    UTS_I_Principal = Column(FLOAT())
    UTS_I_Principal_Situacion = Column(NVARCHAR(30))
    UTS_II_Cabecera_Situacion = Column(NVARCHAR(30))
    UTS_III_RiosMI_Situacion = Column(NVARCHAR(30))
    UTS_IV_RiosMD_Situacion = Column(NVARCHAR(30))
    UTS_GlobalSegura = Column(FLOAT())
    UTS_Global_Segura_Situacion = Column(NVARCHAR(30))
    Alto_Tajo = Column(FLOAT())
    Alto_Tajo_Situacion = Column(NVARCHAR(30))

    @staticmethod
    def get_all_values():
        return DroughtIndices.query.order_by(DroughtIndices.FECHA.desc())

    @staticmethod
    def get_day_values(date, latest=True):
        values = DroughtIndices.query.filter(DroughtIndices.FECHA.in_(date))
        if latest and values.count() == 0:
            values = [DroughtIndices.get_latest_value()]
        return values

    @staticmethod
    def get_range_values(start_date, end_date, latest= True):
        values = DroughtIndices.query.filter(DroughtIndices.FECHA.between(start_date, end_date))\
            .order_by(DroughtIndices.FECHA.desc())
        if latest and values.count() == 0:
            values = [DroughtIndices.get_latest_value()]
        return values
    
    @staticmethod
    def get_latest_value():
        return DroughtIndices.query.order_by(DroughtIndices.FECHA.desc()).first()


class DroughtIndicesSchema(ma.Schema):
    class Meta:
        fields = ('FECHA', 'CUENCA', 'TRASVASE', 'GLOBAL', 'UTE_I_Situacion', 'UTE_I_Escenario', 'UTE_II_Cabecera', 'UTE_II_Situacion', 'UTE_II_Escenario', 'UTE_III_RiosMI', 'UTE_III_Situacion', 'UTE_III_Escenario', 'UTE_IV_RiosMD', 'UTE_IV_Situacion',
                  'UTE_IV_Escenario', 'UTS_I_Principal', 'UTS_I_Principal_Situacion', 'UTS_II_Cabecera_Situacion', 'UTS_III_RiosMI_Situacion', 'UTS_IV_RiosMD_Situacion', 'UTS_GlobalSegura', 'UTS_Global_Segura_Situacion', 'Alto_Tajo', 'Alto_Tajo_Situacion')


drought_index_schema = DroughtIndicesSchema()
drought_indices_schema = DroughtIndicesSchema(many=True)
