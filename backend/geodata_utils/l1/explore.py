#%% Open data

from owslib.wms import WebMapService

OWS_URL= "http://localhost:8000/"
wms = WebMapService(OWS_URL, version='1.3.0')
# %%
