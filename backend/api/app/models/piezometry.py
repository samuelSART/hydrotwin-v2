from sqlalchemy import Column, INTEGER, NVARCHAR, NUMERIC, DATETIME, VARBINARY
from sqlalchemy.orm import column_property
# from geoalchemy2 import Geometry # Commented out as it's not currrently neccesary
from app import db, ma
from marshmallow import fields
from pyproj import Proj, transform


class PiezometryModel(db.Model):
    __bind_key__ = 'PIEZOMETRY_DB'
    __tablename__ = 'VistaPiezometros'
    __table_args__ = {'schema': 'SDEW'}

    # Document variables
    OBJECTID = Column(INTEGER(), primary_key=True)
    COD_CHS = Column(NVARCHAR(10))
    X_50 = Column(NUMERIC())
    Y_50 = Column(NUMERIC())
    X_89 = Column(NUMERIC())
    Y_89 = Column(NUMERIC())
    Z = Column(NUMERIC())
    TOPONIMIA = Column(NVARCHAR(50))
    MUNICIPIO = Column(NVARCHAR(50))
    PROVINCIA = Column(NVARCHAR(50))
    ACUIFERO = Column(NVARCHAR(50))
    MSBT_Nombre = Column(NVARCHAR(250))
    Series_cota = Column(NVARCHAR(200))
    Series_prof = Column(NVARCHAR(200))
    COD_MASA_DEM = Column(NVARCHAR(22))
    FechaFin = Column(DATETIME())
    CODITGE = Column(NVARCHAR(20))
    CODITGE_NUEVO = Column(NVARCHAR(20))
    CodMasa = Column(NVARCHAR(14))
    CodMasaOld = Column(NVARCHAR(5))
    # Shape = Column(String()) # Commented out as it's not currrently neccesary
    GDB_GEOMATTR_DATA = Column(VARBINARY())
    location = column_property('')

    @staticmethod
    def get_piezometers(objectid=None, cod_chs=None):
        if objectid:
            return PiezometryModel.query.filter(PiezometryModel.OBJECTID.in_(objectid))
        elif cod_chs:
            return PiezometryModel.query.filter(PiezometryModel.COD_CHS.in_(cod_chs))
        else:
            return PiezometryModel.query.all()


class PiezometrySchema(ma.Schema):
    class Meta:
        fields = ('COD_CHS', 'Z', 'ACUIFERO', 'MSBT_Nombre',
                  'COD_MASA_DEM', 'CodMasa', 'location')

    location = fields.Method('geometry_to_json')

    def geometry_to_json(self, obj):
        inProj = Proj(init='epsg:25830')
        outProj = Proj(init='epsg:4326')
        x1, y1 = obj.X_89, obj.Y_89
        x2, y2 = transform(inProj, outProj, x1, y1)

        return {
            "type": "Point",
            "coordinates": [x2, y2]
        }


piezometry_schema = PiezometrySchema()
piezometries_schema = PiezometrySchema(many=True)
