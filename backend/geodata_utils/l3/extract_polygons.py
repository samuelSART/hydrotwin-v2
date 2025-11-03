#%% Open data

import rasterio 
import rasterio.features
import rasterio.warp
import json
from decouple import config
import psycopg2

import numpy as np
import fiona

#%% 

shapefile_path = "UDAS.shp"
shape = fiona.open(shapefile_path)
epsg = "25830"


# %% Load data

geom_list = []
# Extract feature shapes and values from the array.
for geom in shape:

    geojson = {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:25830"
                    }
                },
                "features": [geom]
            }

    # Print GeoJSON shapes to stdout.
    print(geom['id'])
    geom_list.append([geom['id'], geojson])

# %%


USER = config('POSTGRES_USER')
PASS = config('POSTGRES_PASSWORD')
DB = config('POSTGRES_DB_2')
HOST = config('POSTGRES_HOST')
PORT = config('POSTGRES_PORT')
# %%


def connect(host,user,password,db,port):
    print('Connecting to the PostgreSQL database...')
    return psycopg2.connect(dbname=db,
                            user=user, 
                            password=password,
                            host=host,
                            port=port)
    

conn = connect(HOST,USER,PASS,DB,PORT)
# %%

def insert_pac_polygon(conn, id, geom, epsg):
    insert = "INSERT INTO line3.UDAS (id,geometry) VALUES(%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), (%s))) ON CONFLICT DO NOTHING;"
    cur = conn.cursor()
    cur.execute(insert, (id, geom,epsg,))
    cur.close()
    conn.commit()


# %%
total = len(geom_list)
i = 0

for id,geojson in geom_list:
    geom = json.dumps(geojson)
    insert_pac_polygon(conn,id,geom,epsg)
    try:
        geom = json.dumps(geojson)
        insert_pac_polygon(conn,id,geom,epsg)
        
        
    except:
        conn.close()
        conn = connect(HOST,USER,PASS,DB,PORT)
        print("Failaso")
# %%
from pyproj import Proj
import geopandas as gpd

data = gpd.read_file(shapefile_path)


p_web = Proj(init='EPSG:4326')

geojson_list = []
# Extract feature shapes and values from the array.
for geom in shape:

    geom_out = geom.copy()
    new_coords = []
    print()
    for coord in geom["geometry"]["coordinates"]:
        aux_coords = []
        for aux in coord:
            print(aux)
            x2, y2 = p_web(*zip(*aux))
            aux_coords.append(list(zip(x2, y2)))
        new_coords.append(aux_coords)
    geom_out["geometry"]["coordinates"] = new_coords
    geojson = {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:4326"
                    }
                },
                "features": [geom_out]
            }
    geojson_list.append(geojson)


# %%
import geopandas as gpd

data = gpd.read_file(shapefile_path)
data.crs = {'init': 'epsg:25830'}
data['geometry'] = data['geometry'].to_crs(epsg=4326)
geom_list = data['geometry'].to_list()
# %%
json_list = []
for geom in geom_list:
        json_list.append(json.loads(gpd.GeoSeries([geom]).to_json()))

# %%
jsonString = json.dumps(json_list)
jsonString = gpd.GeoSeries([geom_list[0]]).to_json()
jsonFile = open("data_1.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

# %%
