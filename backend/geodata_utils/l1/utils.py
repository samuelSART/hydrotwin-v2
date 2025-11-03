
# %% Map mask
import rioxarray
import xarray




def netcd_to_geotiff(path, export_path, bands=None):

    dataset = xarray.open_dataset(path)
    dataset = dataset.rio.write_crs("epsg:4326", inplace=True)
    dataset = dataset.rename({'south_north': 'y','west_east': 'x','XTIME': 'time'})
    dataset = dataset.rio.set_spatial_dims(x_dim="x", y_dim="y")
    
    if bands is None:
        bands = list(dataset.data_vars)
    for band in bands:
        dataset[band].rio.to_raster('{}/{}.tif'.format(export_path,band))
# %%
image = "./wrfout_d01_20220419.nc"
export_path = "."
netcd_to_geotiff(image, export_path)

# %%
