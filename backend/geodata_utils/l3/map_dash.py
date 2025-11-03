# %%



import leafmap
from sqlalchemy import true
m = leafmap.Map()
naip_url = 'http://localhost:8001/wms?'
m.add_wms_layer(
    url=naip_url, layers='line3', styles="irrigation",transparent=True, name='predict', format='image/png', shown=True
)
m