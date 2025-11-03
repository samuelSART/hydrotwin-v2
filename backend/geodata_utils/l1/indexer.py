#%% Open data

import numpy as np
import xarray
#%%

image_rect_path = "/home/VICOMTECH/uotamendi/Projects/hydrotwin/backend/geodata/line1/wrf/2022/05/22/wrfout_d03_20220522-rect.nc"
image_clean_path = "/home/VICOMTECH/uotamendi/Projects/hydrotwin/backend/geodata/line1/wrf/2022/05/22/wrfout_d03_20220522-clean.nc"


rds = xarray.open_dataset(image_clean_path)
#%%

rds["lon"] = (np.array(rds.lon.values) + 180) % 360 - 180  
rds = rds.rio.write_crs(4326,inplace=True).rio.set_spatial_dims(
    x_dim="lon",
    y_dim="lat",
    inplace=True,
).rio.write_coordinate_system(inplace=True)
rds = rds.rename(XTIME= "time", lon="Longitude", lat="Latitude")
rds = rds.rio.reproject("EPSG:4326")
rds = rds.rename(x="Longitude", y="Latitude")

#%%

rds.to_netcdf(image_clean_path)

#%% 
path = "/home/VICOMTECH/uotamendi/Downloads/mini.nc"

ds = xarray.open_dataset(path)
to_drop = []
for name in ds.data_vars:
  if name!="VHM0" and name!="VMDR": to_drop.append(name)
mini = ds.drop_vars(to_drop)
# %%
