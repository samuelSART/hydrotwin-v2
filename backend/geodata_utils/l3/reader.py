#%% Open data
import datacube



dc = datacube.Datacube(app="my_analysis")

dc.list_products()

# %%
ds = dc.load(product="line3",
            resolution=(0.0002217356329508877, -0.0002217356329508877),
            output_crs="EPSG:4326",
            latitude=(-67.70951593127886, -66.24450860437234),
            longitude=( 45.93350161781861, 46.94616825350531))
# %%
dc.index.products.get_by_name("line3").to_dict()
# %%
ds
#
# %%
dc.load(datasets=["8b4c2036-80bd-478c-9582-aa367242e990"])

# %%

# %%
