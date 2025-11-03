
import fiona
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
import geopandas as gpd
import json

def read_shapely(path):
    data = fiona.open(path)
    return data

def simplify_polygon(geom):
    if geom.geom_type == 'MultiPolygon':
        #total_points = sum([len(poly.exterior.coords)  for poly in geom])
        geom_simple = MultiPolygon([poly.simplify(10, preserve_topology=True) for poly in geom.geoms])
        # do multipolygon things.
    elif geom.geom_type == 'Polygon':
        #total_points = len(geom.exterior.coords)
        geom_simple = MultiPolygon([geom.simplify(10, preserve_topology=True)])
    else:
        geom_simple = geom
    return geom_simple
    # imple_points = sum([len(poly.exterior.coords)  for poly in geom_simple])
    # print(" Processed Poly {}".format(prop["COD_UDA"]))
    # print(" Poinst reduced {} Percentage {}".format(total_points - simple_points, ((total_points - simple_points)*100)/total_points ))

def shapely_to_geojson(geom):
    return json.loads(gpd.GeoSeries([geom]).to_json())["features"][0]["geometry"]

def geojson_to_shapely(geom):
    return shape(geom)
