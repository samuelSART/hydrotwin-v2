from flask import Blueprint, request, current_app, jsonify
from app import db
from pyproj import Proj, transform
from datetime import datetime

water_meters_bp = Blueprint('water-meters', __name__)


@water_meters_bp.route('', methods=['GET'])
def get_water_meters():
    try:
        res = db.get_engine(current_app, bind='COUNTERS_DB').execute(
            f'''SELECT
                    s1.CodigoPVYCR,
                    s1.idElementoMedida,
                    dbo.PVYCR_Puntos.DenominacionPunto,
                    s1.Funciona,
                    s1.Fecha_Medida,
                    dbo.PVYCR_Puntos.[X_UTM],
                    dbo.PVYCR_Puntos.[Y_UTM],
                    dbo.PVYCR_Cauces.INSCRIPCION,
                    dbo.PVYCR_Cauces.OtrosExpedientes,
                    dbo.PVYCR_Cauces.NombreTitular,
                    dbo.PVYCR_Cauces.VolumenMaximoAnualLegal_M3,
                    dbo.PVYCR_Cauces.MunicipioToma,
                    dbo.PVYCR_Cauces.DenominacionCauce
                FROM 
                    dbo.PVYCR_Puntos
                INNER JOIN
                (
                    SELECT
                    s.CodigoPVYCR,
                    s.Fecha_Medida,
                    s.Funciona,
                    s.idElementoMedida
                    FROM(
                        SELECT
                        dbo.PVYCR_DatosMotores.CodigoPVYCR,
                        dbo.PVYCR_DatosMotores.Funciona,
                        dbo.PVYCR_DatosMotores.Fecha_Medida,
                        dbo.PVYCR_DatosMotores.idElementoMedida,
                        max_date=MAX(dbo.PVYCR_DatosMotores.Fecha_Medida) OVER(PARTITION BY dbo.PVYCR_DatosMotores.CodigoPVYCR)
                        FROM
                        dbo.PVYCR_DatosMotores
                    ) AS s
                    WHERE
                    s.Fecha_Medida=max_date
                ) as s1
                ON
                    (dbo.PVYCR_Puntos.CodigoPVYCR=s1.CodigoPVYCR)
                INNER JOIN
                    dbo.PVYCR_Cauces ON dbo.PVYCR_Puntos.CodigoCauce=dbo.PVYCR_Cauces.CodigoCauce
                ORDER BY
                    dbo.PVYCR_Puntos.CodigoPVYCR
            ''').all()

        inProj = Proj(init='epsg:25830')
        outProj = Proj(init='epsg:4326')

        ###
        # Filter data and transform coordinates
        ###
        data = []
        filtered_data = []
        x_coord, y_coord = [], []
        for cursor in res:
            X_UTM = None if 5 >= len(cursor) else cursor[5]
            Y_UTM = None if 6 >= len(cursor) else cursor[6]
            if X_UTM is not None or Y_UTM is not None:
                # long, lat = transform(inProj, outProj, cursor[5], cursor[6])
                x_coord.append(cursor[5])
                y_coord.append(cursor[6])
                filtered_data.append(cursor)

        long, lat = transform(inProj, outProj, x_coord, y_coord)
        for index, water_meter_data in enumerate(filtered_data):
            data.append({
                "CodigoPVYCR": None if 0 >= len(water_meter_data) else water_meter_data[0],
                "idElementoMedida": None if 1 >= len(water_meter_data) else water_meter_data[1],
                "DenominacionPunto": None if 2 >= len(water_meter_data) else water_meter_data[2],
                "Funciona": None if 3 >= len(water_meter_data) else water_meter_data[3],
                "Fecha_Medida": None if 4 >= len(water_meter_data) else water_meter_data[4],
                "location": {
                    "coordinates": [long[index], lat[index]],
                    "type": "Point"
                },
                "INSCRIPCION": None if 7 >= len(water_meter_data) else water_meter_data[7],
                "OtrosExpedientes": None if 8 >= len(water_meter_data) else water_meter_data[8],
                "NombreTitular": None if 9 >= len(water_meter_data) else water_meter_data[9],
                "VolumenMaximoAnualLegal_M3": None if 10 >= len(water_meter_data) else water_meter_data[10],
                "MunicipioToma": None if 11 >= len(water_meter_data) else water_meter_data[11],
                "DenominacionCauce": None if 12 >= len(water_meter_data) else water_meter_data[12]
            })

        return jsonify({'status': 200, 'data': data, 'ok': True})

    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'text': str(e), 'ok': False}), 500


@water_meters_bp.route('/get-values', methods=['POST'])
def get_values():

    data = request.get_json()
    start_date = data.get(
        'start_date') if data and 'start_date' in data else None
    end_date = data.get(
        'end_date') if data and 'end_date' in data else None
    water_meter_id = data.get(
        'water_meter_id') if data and 'water_meter_id' in data else None

    if start_date is None or end_date is None or water_meter_id is None:
        return jsonify({'status': 400, 'title': 'Error', 'detail': 'Missing params (start_date, end_date or water_meter_id).', 'ok': False}), 400

    try:
        res = db.get_engine(current_app, bind='COUNTERS_DB').execute(
            f'''SELECT 
                    dbo.PVYCR_DatosMotores.Fecha_Medida,
                    dbo.PVYCR_DatosMotores.LecturaContador_M3,
                    dbo.PVYCR_DatosMotores.CodigoPVYCR
                FROM 
                    dbo.PVYCR_DatosMotores
                WHERE 
                    (dbo.PVYCR_DatosMotores.CodigoPVYCR = '{water_meter_id}') and 
                    (dbo.PVYCR_DatosMotores.Fecha_Medida >= '{start_date}') and
                    (dbo.PVYCR_DatosMotores.Fecha_Medida <= '{end_date}')
                ORDER BY 
                    dbo.PVYCR_DatosMotores.Fecha_Medida DESC
            ''')

        data = [
            {
                "_time": None if 0 >= len(cursor) else int(datetime.strptime(str(cursor[0]), '%Y-%m-%d %H:%M:%S').timestamp() * 1000),
                "_value": None if 1 >= len(cursor) else cursor[1],
                "variableCode":None if 2 >= len(cursor) else cursor[2]
            }
            for cursor in res
        ]

        return jsonify({'status': 200, 'data': data, 'ok': True})
    except Exception as e:
        return jsonify({'status': 500, 'title': 'Error', 'text': str(e), 'ok': False}), 500
