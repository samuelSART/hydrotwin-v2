# %%

import pandas as pd
import database_utils as db
sai_file = "./ElementosSAIH.XLSX"
Qeco_file = "./Qeco.csv"
Dams_file = "./Dams.csv"
Crop_file = "./Crop.csv"
Emission_file = "./Emission.csv"
UDU_file = "./UDU.csv"
UDI_file = "./UDI.csv"
UDRG_file = "./UDRG.csv"
Humedal_file = "./Humedal.csv"
UD_Annual = "./UD_Annual.csv"
UD_Monthly = "./UD_Monthly.csv"
EPSG = "25830"


# %%

xls = pd.ExcelFile(sai_file)
puntos_control = pd.read_excel(xls, 'PuntosControl', header=1)
puntos_medicion = pd.read_excel(xls, 'PuntosMedición', header=1)
variables = pd.read_excel(xls, 'VariablesEnPuntosMed', header=1)


# %%

def process_control_points(dataset):
    for index, row in dataset.iterrows():
        code = row['CodPuntoControl']
        denomination = row['Denominación']
        municipality = row['Municipio']
        province = row['Provincia']
        typology = row['CodTipologiaPuntoControl']
        description = row['DescripciónTipologiaPuntoControl']
        x = row['XETRS89']
        y = row['YETRS89']
        conn = db.connect()
        db.insert_control_point(
            conn, code, denomination, municipality, province, typology, description, x, y, EPSG)
        conn.close()
        print("Point nº {} uploaded".format(index))


process_control_points(puntos_control)
# %%


def process_measurement_points(dataset):
    for index, row in dataset.iterrows():
        code = row['CodPuntoMedición']
        denomination = row['Denominación']
        control_point = row['CodPuntoControl']
        typology = row['CodTipologíaPuntoMedición']
        description = row['DenominaciónTipologíaPuntoMedición']
        x = row['XETRS89']
        y = row['YETRS89']
        conn = db.connect()
        db.insert_measurement_point(
            conn, code, control_point, denomination, typology, description, x, y, EPSG)
        conn.close()
        print("Point nº {} uploaded".format(index))


process_measurement_points(puntos_medicion)
# %%


def process_variable(dataset):
    for index, row in dataset.iterrows():
        code = row['CodVariableHidrológica']
        measurement_point = row['CodPuntoMedición']
        typology = row['CodTipologíaVariableHidrológica']
        description = row['DenominaciónTipologíaVariable']
        conn = db.connect()
        db.insert_variable(conn, code, measurement_point,
                           typology, description)
        conn.close()
        print("Point nº {} uploaded".format(index))


process_variable(variables)

# %%


def process_environmental_flow():
    df = pd.read_csv(Qeco_file)
    df.dropna(inplace=True)

    conn = db.connect()
    db.insert_dataframe(conn, df, 'environmental_flow')
    conn.close()


process_environmental_flow()
# %%


def process_dams():
    df = pd.read_csv(Dams_file)
    df.fillna(0, inplace=True)

    conn = db.connect()
    db.insert_dataframe(conn, df, 'dam')
    conn.close()


process_dams()

# %%


def process_crop():
    df = pd.read_csv(Crop_file)

    conn = db.connect()
    db.insert_dataframe(conn, df, 'crop')
    conn.close()


process_crop()

# %%


def process_UDU():
    df = pd.read_csv(UDU_file)

    for index, row in df.iterrows():
        code = row['code']
        type = row['type']
        x = row['XETRS89']
        y = row['YETRS89']
        name = row['name']
        conn = db.connect()
        db.insert_demand_unit(conn, code, type, x, y, name, EPSG)
        conn.close()
        print("UDU nº {} uploaded".format(index))


process_UDU()
# %%


def process_UDI():
    df = pd.read_csv(UDI_file)

    for index, row in df.iterrows():
        code = row['code']
        type = row['type']
        x = row['XETRS89']
        y = row['YETRS89']
        name = row['name']
        conn = db.connect()
        db.insert_demand_unit(conn, code, type, x, y, name, EPSG)
        conn.close()
        print("UDI nº {} uploaded".format(index))


process_UDI()

# %%


def process_UDRG():
    df = pd.read_csv(UDRG_file)

    for index, row in df.iterrows():
        code = row['code']
        type = row['type']
        x = row['XETRS89']
        y = row['YETRS89']
        name = row['name']
        conn = db.connect()
        db.insert_demand_unit(conn, code, type, x, y, name, EPSG)
        conn.close()
        print("UDRG nº {} uploaded".format(index))


process_UDRG()
# %%


def process_Humedal():
    df = pd.read_csv(Humedal_file)

    for index, row in df.iterrows():
        code = row['code']
        type = row['type']
        x = row['XETRS89']
        y = row['YETRS89']
        name = row['name']
        conn = db.connect()
        db.insert_demand_unit(conn, code, type, x, y, name, EPSG)
        conn.close()
        print("Humedal nº {} uploaded".format(index))


process_Humedal()