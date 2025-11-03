#%%
from datetime import date
import xarray 
import rioxarray
import numpy as np
import os 
#%%
file="/home/VICOMTECH/uotamendi/Projects/hydrotwin/backend/geodata/L1/OUT/PREDICC_S/2022/09/07/WRF_20220907-rect-daily.nc"
image = "/home/VICOMTECH/uotamendi/Projects/hydrotwin/backend/geodata/L1/OUT/PREDICC_M/2022/10/16/MidTerm-WGS84.nc"



save_folder = os.path.dirname(file)
filename_prefix = os.path.basename(file).split(".")[0]

rds = xarray.open_dataset(file)
rds.coords['lon'] = (rds.coords['lon'] + 180) % 360 - 180
rds = rds.rename(XTIME= "time")
#%%
tif_files = []
d_time = rds['time'].values
for t in d_time:
    rds_time = rds.sel(time=t)
    rds_time = rds_time.rio.set_spatial_dims('lon', 'lat')
    rds_time.rio.write_crs(4326)
    date_str = "".join(np.datetime_as_string(t, unit='D').split("-"))
    path = os.path.join(save_folder, filename_prefix + "_{}.tif".format(date_str))
    
    rds_time.rio.to_raster(path)
    tif_files.append(path)


#Saving the file
# %%
