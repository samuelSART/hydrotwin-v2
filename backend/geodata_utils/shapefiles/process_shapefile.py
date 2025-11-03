#%% 

from fileinput import filename
import glob
import utils
import database_utils as db
import json
import os

UD_folder = "./Demandas/"
superficial_folder = "./Masas/Superficiales/"
subterraneas_folder = "./Masas/Subterraneas/"
acuiferos_folder = "./Masas/Acuiferos/"

EPSG = "25830"

def find_files(path):
    return glob.glob(path+"/**/*.shp",recursive = True)

def process_polygon(polygon):
   
    geom = utils.geojson_to_shapely(polygon["geometry"])
    simple_geom = utils.simplify_polygon(geom)
    simple_poly = utils.shapely_to_geojson(simple_geom)
    simple_poly["properties"] = polygon["properties"]
    simple_poly["crs"] = {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:{}".format(EPSG)
                    }
                }
    return simple_poly

def process_UDA(path, filename="UDA"):
    file = os.path.join(path,filename+".shp")
    data = utils.read_shapely(file)
    type = "agriculture"
    for e, poly in enumerate(data):
        code = poly["properties"]["COD_UDA"]
        name = poly["properties"]["Nombre_UDA"]
        simplified_poly = process_polygon(poly)
        conn = db.connect()
        db.insert_ud_polygon(conn, code, type, json.dumps(simplified_poly), EPSG, name)
        conn.close()
        print("Polygon n{} uploaded".format(e))
    print("Finished processing")


def process_superficial(path, filename="AW"):
    file = os.path.join(path,filename+".shp")
    data = utils.read_shapely(file)
    type = "superficial"
    for e, poly in enumerate(data):
        EUMSPFCOD = poly["properties"]["EUMSPFCOD"]
        code = poly["properties"]["MSPF_EM_CD"]
        name = poly["properties"]["MSPF_NAME"]
        category = poly["properties"]["CATEGORIA"]
        simplified_poly = process_polygon(poly)
        conn = db.connect()
        db.insert_superficial_polygon(conn, code, type, EUMSPFCOD, name, category, json.dumps(simplified_poly), EPSG)
        conn.close()
        print("Polygon n{} uploaded".format(e))
    print("Finished processing")


def process_subterraneas(path, filename="Subterraneas"):
    file = os.path.join(path,filename+".shp")
    data = utils.read_shapely(file)
    type = "underground"
    category = " ".join(filename.split("_"))
    for e, poly in enumerate(data):
        code = poly["properties"]["Cod_MAS"]
        EUMSBTCOD = poly["properties"]["EUMSBTCOD"]
        name = poly["properties"]["Nombre_MAS"]
        simplified_poly = process_polygon(poly)
        conn = db.connect()
        db.insert_underground_polygon(conn, code, type, EUMSBTCOD, name, category, json.dumps(simplified_poly), EPSG)
        conn.close()
        print("Polygon n{} uploaded".format(e))
    print("Finished processing")

def process_acuiferos(path, filename="Acuiferos"):
    file = os.path.join(path,filename+".shp")
    data = utils.read_shapely(file)
    type = "aquifer"
    category = " ".join(filename.split("_"))
    for e, poly in enumerate(data):
        code = poly["properties"]["COD_ACU"]
        try:
            superpos = poly["properties"]["Superposic"]
        except:
            superpos = None
        name = poly["properties"]["NOMACU"]
        simplified_poly = process_polygon(poly)
        conn = db.connect()
        db.insert_aquifer_polygon(conn, code, type, superpos, name, category, json.dumps(simplified_poly), EPSG)
        conn.close()
        print("Polygon n{} uploaded".format(e))
    print("Finished processing")
# %%


process_UDA(UD_folder)

for file in find_files(superficial_folder):
    filename = os.path.basename(file).split(".")[0]
    print(filename)
    process_superficial(superficial_folder, filename=filename)


for file in find_files(subterraneas_folder):
    filename = os.path.basename(file).split(".")[0]
    print(filename)
    process_subterraneas(subterraneas_folder, filename=filename)


for file in find_files(acuiferos_folder):
    filename = os.path.basename(file).split(".")[0]
    print(filename)
    process_acuiferos(acuiferos_folder, filename=filename)


# %%
