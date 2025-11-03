import logging
import geopandas
from datacube.api.query import Query
from datacube.utils.geometry import Geometry
from datacube.utils.geometry import CRS
from shapely.geometry import shape


class PolygonDataLoader:
    def __init__(self, datacube, output_epsg, input_epsg, resolution, product, product_query={}):
        self.datacube = datacube
        self.output_crs = CRS('EPSG:{}'.format(output_epsg))
        # self.resolution = (-resolution*0.00000898311, resolution*0.00000898311) # EPGS: 4326
        self.resolution = (-resolution, resolution)
        self.query_crs = CRS('EPSG:{}'.format(input_epsg))  # 4326
        self.product = product
        self.product_query = product_query
    
    def create_querys(self, polygon):
        odc_Polygon = Geometry(polygon, crs=self.query_crs)
        odc_Polygon = odc_Polygon.to_crs(self.output_crs)
       
        query = Query(product=self.product,
                        geopolygon=odc_Polygon
                    )
        return query
    
    def datacube_load(self, polygon):
        query = self.create_querys(polygon)
        empty = False
        logging.debug(query.search_terms)
        data = self.datacube.load(output_crs=self.output_crs,
                                        resolution=self.resolution,
                                        **query.search_terms,
                                        **self.product_query)
        if self.is_dataset_empty(data):
            logging.debug("DataCube Load returned an empty Dataset for {}.".format(self.product))
            data = None
            empty = True
        return data, empty
    
    def shape_data(self, polygon, data, only_mean):
        polygon_shape = shape(polygon)
        centroid = polygon_shape.centroid.coords[0]
        gd_polygon = geopandas.GeoSeries(polygon_shape).set_crs(
            self.query_crs).to_crs(self.output_crs)
        
        gd_polygon = geopandas.GeoDataFrame(geometry=gd_polygon)
        data_df = data.to_dataframe().reset_index()
        coords = ['x', 'y'] if str(self.output_crs) == "3042" else ['latitude', 'longitude']
        
        gdf = geopandas.GeoDataFrame(data_df,geometry=geopandas.points_from_xy(data_df[coords[1]], data_df[coords[0]])).set_crs(self.output_crs)
        
        gdf['geometry'] = gdf.apply(lambda x: x.geometry.buffer(self.resolution[1]/2,cap_style=3), axis=1)
        
        from geopandas.tools import sjoin
        pointInPolys = sjoin(gdf, gd_polygon, how='left')
        
        data_df = pointInPolys[pointInPolys['index_right'].notna()]
        data_df = data_df.drop(['index_right'], axis=1)
        
        if only_mean:
            data_df = data_df.drop(coords, axis=1)
            data_df = data_df.groupby('time').mean()
            data_df[coords[0]] = centroid[0]
            data_df[coords[1]] = centroid[1]
            data_df = data_df.reset_index()
            data_df = geopandas.GeoDataFrame(data_df,geometry=geopandas.points_from_xy(data_df[coords[1]], data_df[coords[0]])).set_crs(self.output_crs)
        data_df['time'] = data_df['time'].astype(str)
        return data_df
    
    def load_polygon_data(self, polygon, only_mean):
        raw_data, empty = self.datacube_load(polygon)
        if empty:
            return raw_data, empty  
        data = self.shape_data(polygon, raw_data, only_mean)
        return data, empty
    
    def is_dataset_empty(self, data):
        try:
            # Check dataset empty
            checks_for_empty = [
                lambda x: len(x.dims) == 0,  # Dataset has no dimensions
                lambda x: len(x.data_vars) == 0  # Dataset no variables
            ]
            for f in checks_for_empty:
                if f(data) == True:
                    return True
            return False
        except:
            return True

