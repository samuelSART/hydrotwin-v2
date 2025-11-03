#%% Open data

import rasterio 
import rasterio.features
import rasterio.warp
import geopandas as gpd

# %% Load data

cp = rasterio.open("/home/VICOMTECH/uotamendi/Projects/hydrotwin/backend/geodata/L3/OUT/HISTORICAL/2022/10/segura_202211_Crop_classification_num_20m.tif")

# %% Map mask

def get_poly_coords(raster_path: str, crs: str)-> list:
    from shapely.geometry import box, mapping
    import rasterio
    raster = rasterio.open(raster_path)
    bounds = raster.bounds
    raster.close()
    geom = box(*bounds)

    from pyproj import Transformer, CRS
    inProj = CRS.from_string(crs)
    outProj = CRS.from_string('epsg:4326')
    transformer = Transformer.from_crs(inProj,outProj)
    lat_begin, lon_begin = transformer.transform(bounds.left, bounds.bottom)

    lat_end, lon_end = transformer.transform(bounds.right, bounds.top)
    
    geometry = [[list(x) for x in mapping(geom)['coordinates'][0]]]

    return geometry, lat_begin, lon_begin,  lat_end, lon_end 
    
get_poly_coords(image_cwsi,'epsg:4326')
# %%
import geopandas as gpd
gdf = gpd.read_file(vector)
# %%
cwsi = rasterio.open(image_cwsi)
# %%
