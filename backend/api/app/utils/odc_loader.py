import pandas as pd

from .geoutils import dc
from .odc.polygonDataLoader import PolygonDataLoader
from .odc.dataLoader import process_polygon_data


def load_geometry_data( geometry_list: list,
                        product: str,
                        output_epsg: int = "3042", 
                        input_epsg: int = "3042", 
                        resolution: int = 20, 
                        product_query: dict = {},
                        only_mean: bool = False):

    loader = PolygonDataLoader(dc, output_epsg, input_epsg, resolution, product, product_query=product_query)
    return process_polygon_data(loader, geometry_list, only_mean)


def load_geometry_stats( geometry_list: list,
                        product: str,
                        output_epsg: int = "3042", 
                        input_epsg: int = "3042", 
                        resolution: int = 20, 
                        product_query: dict = {},
                        only_mean: bool = False):
    loader = PolygonDataLoader(dc, output_epsg, input_epsg, resolution, product, product_query=product_query)
    result, empty = process_polygon_data(loader, geometry_list, only_mean)
    if empty:
        return None, True
    #geometry_json = json.loads(gpd.GeoSeries([result["geometry"][0]]).to_json())
    result.drop(['spatial_ref','longitude','latitude','geometry'], axis=1, inplace=True)
    df = pd.DataFrame(result)
    variableCode = df.columns[1]
    df.columns = ["_time","_value"]
    df['_value'] = df['_value'].fillna(0)
    df["variableCode"] = variableCode
    df["_time"] = ((pd.to_datetime(df['_time'], format="%Y-%m-%d") - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')) * 1000
    stats = df.to_dict(orient="records")
    return stats, False

