#%%
import mikeio
import re

# %%
file = "/home/VICOMTECH/uotamendi/Projects/hydrotwin/backend/geodata/L2/OUT/PREDICC_S/2022/SHE_GLOBAL_Ver02DetailedTS_M11.dfs0"
# %%
ds = mikeio.read(file)
# %%
df = ds.to_dataframe()
old_columns = list(df.columns)
# %%
new_columns = []
for col in old_columns:
    value = re.search('\(([^)]+)\)', col)
    if value:
        id = value.group(1).split(" ")[-1]
    else:
        id = 'None'
    new_columns.append(id)
# %%
df2 = df.set_axis(new_columns, axis=1, inplace=False)
# %%

# %%
from owslib.wms import WebMapService
OWS_URL = 'http://localhost:8000/'
    
wms = WebMapService(OWS_URL, version='1.3.0')

layer = wms['evapotranspiration']
# %%
