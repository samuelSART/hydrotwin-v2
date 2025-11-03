import os
import datacube
import logging
import numpy as np
import rasterio
import xarray
from flask import current_app
from shapely.geometry import box, mapping
from pyproj import Transformer, CRS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

dc = datacube.Datacube(
    config=current_app.config['DC_CONFIG'], env='default', app='chs', validate_connection=False)


def init_odc() -> bool:
    try:
        return dc.index.init_db()
    except Exception as e:
        logging.error(f'An error occurred trying to initialize ODC: {e}')
        raise


def add_metadata(metadata_file: str) -> bool:
    try:
        metadata = list(datacube.utils.documents.load_documents(
            path=metadata_file))[0]
        dc.index.metadata_types.update_document(metadata)
        return True
    except Exception as e:
        logging.error(
            f'An error occurred trying to add metadata type file \'{metadata_file}\': {e}')
        raise


def add_product(metadata_file: str) -> bool:
    try:
        dc.index.products.add_document(
            list(datacube.utils.documents.load_documents(path=metadata_file))[0])
        return True
    except Exception as e:
        logging.error(
            f'An error occurred trying to add product file \'{metadata_file}\': {e}')
        return False


def update_product(metadata_file: str) -> bool:
    try:
        dc.index.products.update_document(list(datacube.utils.documents.load_documents(path=metadata_file))[0], allow_unsafe_updates=True)
        return True
    except Exception as e:
        logging.error(f'An error occurred trying to update product file \'{metadata_file}\': {e}')
        return False


def add_product_doc(product: dict) -> bool:
    try:
        dc.index.products.from_doc(product)
        return True
    except Exception as e:
        logging.error(f'An error occurred trying to add product: {e}')
        raise


def add_dataset(metadata_file: str, product: str) -> bool:
    try:
        dataset = list(datacube.utils.documents.load_documents(
            path=metadata_file))[0]
        dataset_type = dc.index.products.get_by_name(product)
        file_uri = datacube.utils.uris.uri_resolve(base=current_app.config['DATA_FOLDER'], path=metadata_file)
        dc.index.datasets.add(datacube.model.Dataset(product=dataset_type, metadata_doc=dataset, uris=[file_uri]))
        return True
    except Exception as e:
        logging.error(
            f'An error occurred trying to add dataset \'{metadata_file}\': {e}')
        return False


def find_dataset(root: str, file_name: str) -> list:
    import glob
    files = glob.glob(root+"/**/"+file_name, recursive=True)
    return files


def archive_dataset(id: str) -> bool:
    try:
        dc.index.datasets.archive(ids=[id])
        logging.debug(f'Archive dataset id \'{id}\'')
        return True
    except Exception as e:
        logging.error(
            f'An error occurred trying to archive dataset id \'{id}\': {e}')
        return False


def get_poly_coords(raster_path: str, crs: str) -> list:
    raster = rasterio.open(raster_path)
    bounds = raster.bounds
    raster.close()
    geom = box(*bounds)

    inProj = CRS.from_string(crs)
    outProj = CRS.from_string('epsg:4326')
    transformer = Transformer.from_crs(inProj, outProj)
    lat_begin, lon_begin = transformer.transform(bounds.left, bounds.bottom)
    lat_end, lon_end = transformer.transform(bounds.right, bounds.top)

    geometry = [[list(x) for x in mapping(geom)['coordinates'][0]]]

    return geometry, lat_begin, lon_begin, lat_end, lon_end


def netcdf_clean(raster_path: str):
    rds = xarray.open_dataset(raster_path)
    if "time" in list(rds.variables):
        return raster_path
    filename = os.path.basename(raster_path).split(".")
    new_filename = filename[0] + "_clean." + filename[1]
    new_path = os.path.dirname(raster_path) + "/" + new_filename
    rds["lon"] = (np.array(rds.lon.values) + 180) % 360 - 180

    rds = rds.rio.set_spatial_dims('lon', 'lat')
    rds.rio.write_crs(4326)
    rds = rds.rename(XTIME="time")
    rds.to_netcdf(new_path)
    return new_path


def netcdf_monthly_clean(raster_path: str):
    rds = xarray.open_dataset(raster_path)
    if "lon" in list(rds.variables):
        return raster_path
    filename = os.path.basename(raster_path).split(".")
    new_filename = filename[0] + "_clean." + filename[1]
    new_path = os.path.dirname(raster_path) + "/" + new_filename
    rds = rds.rename(longitude="lon", latitude="lat")
    rds["lon"] = (np.array(rds.lon.values) + 180) % 360 - 180

    rds = rds.rio.set_spatial_dims('lon', 'lat')
    rds.rio.write_crs(4326)

    rds.to_netcdf(new_path)
    return new_path


def geotif_get_properties(raster_path: str):
    import rasterio
    raster = rasterio.open(raster_path)
    transform = list(raster.meta['transform'])
    shape = [raster.meta["width"], raster.meta["height"]]

    bounds = raster.bounds
    # if transform:
    #     original_crs = str(raster.crs)
    #     inProj = CRS.from_string(original_crs)
    #     outProj = CRS.from_string('epsg:4326')
    #     transformer = Transformer.from_crs(inProj,outProj)
    #     lat_min, lon_min = transformer.transform(bounds.left, bounds.bottom)
    #     lat_max, lon_max = transformer.transform(bounds.right, bounds.top)
    # else:
    lat_max = bounds.top
    lat_min = bounds.bottom

    lon_max = bounds.right
    lon_min = bounds.left

    polygon = [[
        [lon_min, lat_min],
        [lon_max, lat_min],
        [lon_max, lat_max],
        [lon_min, lat_max],
        [lon_min, lat_min]
    ]]

    return polygon, shape, transform


def netcdf_get_properties(raster_path: str, variable: str = "T2"):
    import netCDF4 as nc
    import numpy as np
    #from osgeo import gdal

    ds = nc.Dataset(raster_path)
    time_serie = ds.variables['time']
    dtime = nc.num2date(time_serie[:], time_serie.units)

    lat = np.array(ds.variables['lat'])[:]
    lat_max = lat.max()
    lat_min = lat.min()

    lon = np.array(ds.variables['lon'])[:]
    lon_max = lon.max()
    lon_min = lon.min()

    polygon = [[
        [lon_min, lat_min],
        [lon_max, lat_min],
        [lon_max, lat_max],
        [lon_min, lat_max],
        [lon_min, lat_min]
    ]]
    shape = list(ds.variables[variable].shape)[1:]

    xds = xarray.open_dataset(raster_path)
    transform = list(xds.rio.transform())

    #imageinfo = gdal.Open(file)
    #projection = imageinfo.GetProjection()

    return polygon, shape, transform, dtime


def inflates_geometry(geometry, distance):
    import geopandas
    from shapely.geometry import shape

    gd_polygon = geopandas.GeoSeries(shape(geometry), crs=4326).to_crs(3857)
    gd_polygon = gd_polygon.buffer(distance/2).to_crs(25830)

    return gd_polygon[0]


def netcdf_to_geotiff(file):
    import xarray
    import numpy as np
    import os
    save_folder = os.path.dirname(file)
    filename_prefix = os.path.basename(file).split(".")[0]

    rds = xarray.open_dataset(file)
    if "valid_time" in list(rds.variables):
        rds = rds.drop_vars('valid_time')
    if "spatial_ref" in list(rds.variables):
        rds = rds.drop_vars('spatial_ref')
    if "lon" not in list(rds.variables):
        rds = rds.rename(longitude="lon", latitude="lat")

    rds.coords['lon'] = (rds.coords['lon'] + 180) % 360 - 180
    if "time" not in list(rds.variables):
        rds = rds.rename(XTIME="time")
    tif_files = []
    dates = []
    d_time = rds['time'].values

    for t in d_time:
        rds_time = rds.sel(time=t)
        rds_time["lon"] = rds_time["lon"].rio.write_nodata(np.nan)
        rds_time["lat"] = rds_time["lat"].rio.write_nodata(np.nan)
        rds_time = rds_time.rio.set_spatial_dims('lon', 'lat')
        rds_time.rio.write_crs(4326)
        date = np.datetime_as_string(t, unit='D')
        date_str = "".join(date.split("-"))
        path = os.path.join(save_folder, filename_prefix +
                            "_{}.tif".format(date_str))
        rds_time.rio.to_raster(path)
        tif_files.append(path)
        dates.append(date)

    return tif_files, dates


DATA_FOLDER = current_app.config['DATA_FOLDER']
L3_SHORT_FOLDER = DATA_FOLDER + "/L3/OUT/PREDICC_S"
L3_MID_FOLDER = DATA_FOLDER + "/L3/OUT/PREDICC_M"
L3_HISTORICAL_FOLDER = DATA_FOLDER + "/L3/OUT/HISTORICAL"
L1_DAILY_FOLDER = DATA_FOLDER + "/L1/OUT/PREDICC_S"
L1_MONTHLY_FOLDER = DATA_FOLDER + "/L1/OUT/PREDICC_M"

def find_uda_stats(date: datetime, product: str):
    import pandas as pd

    ''' Find the UDA stats csv file for a given date and product

    Args:
        date (datetime): date
        product (str): product name

    Returns:
        pandas.DataFrame: UDA stats
    '''

    if product == "wrf_monthly" or product == "wrf_daily":
        return None
    file = find_uda_stats_file(date, product)
    if file is not None:
        df = pd.read_csv(file)
        df.columns = ["uda", "date",  "mean", "sum"]
        df["date"] = df["date"].astype(str)
        df = df[(df["date"] == date.strftime("%Y%m%d")) | (df["date"] == date.strftime("%Y%m"))]
        return df
    return None


def find_uda_stats_file(date: datetime, product: str) -> str:
    import glob
    ''' Find the UDA stats csv file for a given date and product

    Args:
        date (datetime): date
        product (str): product name

    Returns:
        str: UDA stats file path
    '''
    MAX_DELAY_DAYS = 15
    MAX_DELAY_MONTHS = 6
    if product == "evapotranspiration" or product == "waterdemand":
        folder = L3_SHORT_FOLDER
        prod = "ET" if product == "evapotranspiration" else "WD"
        files = glob.glob(
            f"{folder}/{date.strftime('%Y/%m/%d')}/{prod}*.csv", recursive=True)
        if len(files) > 0:
            return files[0]
        for i in range(MAX_DELAY_DAYS):
            aux_date = date - timedelta(days=i)
            files = glob.glob(
                f"{folder}/{aux_date.strftime('%Y/%m/%d')}/{prod}*.csv", recursive=True)
            if len(files) > 0:
                return files[0]
    elif product == "evapotranspiration_monthly" or product == "waterdemand_monthly":
        folder = L3_MID_FOLDER
        prod = "ET" if product == "evapotranspiration" else "WD"
        files = glob.glob(
            f"{folder}/{date.strftime('%Y/%m')}/{prod}*.csv", recursive=True)
        if len(files) > 0:
            return files[0]
        for i in range(MAX_DELAY_MONTHS):
            aux_date = date - relativedelta(months=i)
            files = glob.glob(
                f"{folder}/{aux_date.strftime('%Y/%m')}/{prod}*.csv", recursive=True)
            if len(files) > 0:
                return files[0]
    elif product == "biomass":
        folder = L3_HISTORICAL_FOLDER
        prod = "Biomass"
        files = glob.glob(
            f"{folder}/{date.strftime('%Y/%m')}/{prod}*.csv", recursive=True)
        if len(files) > 0:
            return files[0]
    elif product == "wrf_daily":
        folder = L1_DAILY_FOLDER
        files = glob.glob(
            f"{folder}/{date.strftime('%Y/%m/%d')}/*estaciones.csv", recursive=True)
        if len(files) > 0:
            return files[0]
        for i in range(MAX_DELAY_DAYS):
            aux_date = date - relativedelta(days=i)
            files = glob.glob(
                f"{folder}/{aux_date.strftime('%Y/%m/%d')}/*estaciones.csv", recursive=True)
            if len(files) > 0:
                return files[0]
    elif product == "wrf_monthly":
        folder = L1_MONTHLY_FOLDER
        files = glob.glob(
            f"{folder}/{date.strftime('%Y/%m/%d')}/*estaciones.csv", recursive=True)
        if len(files) > 0:
            return files[0]
        for i in range(MAX_DELAY_MONTHS * 31):
            aux_date = date - relativedelta(days=i)
            files = glob.glob(
                f"{folder}/{aux_date.strftime('%Y/%m/%d')}/*estaciones.csv", recursive=True)
            if len(files) > 0:
                return files[0]
    else:
        return None
    return None


def find_raster_file(date: datetime, product: str) -> str:
    import yaml
    ''' Find the raster file for a given date and product

    Args:
        date (datetime): date
        product (str): product name

    Returns:
        str: raster file path
    '''
    datasets = dc.find_datasets(product=product,
                                time=(date.strftime("%Y-%m-%d"),
                                      date.strftime("%Y-%m-%d")))
    if len(datasets) > 0:
        yaml_file = datasets[0].local_path
        data = yaml.load(open(yaml_file), Loader=yaml.FullLoader)
        try:
            measurements = data["measurements"]
            band = measurements.popitem()
            path = band[1]["path"]
            path_splt = path.split("file://")
            if len(path_splt) > 1:
                path = path_splt[1]
            else:
                path = path_splt[0]
            if os.path.isfile(path):
                return path
        except Exception as e:
            print(e)
            pass
    return None
