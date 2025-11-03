#%% Open data

from datetime import datetime
import os

import rasterio 

def init_odc(host: str, database: str, user: str, password: str, port: int = 5432):
    config_text = '''
    [{}]
    db_database:{}
    db_hostname:{}
    db_username:{}
    db_password:{}
    db_port:{}
        '''.format("default", database, host, user, password,port)
    with open('./datacube.conf', 'w') as file:
        file.write(config_text)
    import subprocess
    subprocess.Popen(['datacube', 'system', 'init'])
      
    import datacube
    dc = datacube.Datacube()
    dc.list_products()
    return True





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
    


def generate_metadata(path_raster: str, template_file: str, metadata:str,final_path:str) -> list:
    import uuid 
    import subprocess
    


    with open(template_file, 'r') as f:
            template = f.read()


    file_path = os.path.abspath(path_raster)
    filename = os.path.basename(file_path).split(".")[0]
    folder_path = os.path.dirname(file_path) + "/metadata"
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)
    metadata_file = folder_path + "/{}.yaml".format(filename)

    if os.path.isfile(metadata_file):
        import yaml 
        from yaml.loader import SafeLoader
        with open(metadata_file) as f:
            data = yaml.load(f, Loader=SafeLoader)
        old_uuid = data['id']
        print("Archiving metadata uuid: {}".format(old_uuid))
        subprocess.Popen(['datacube', 'dataset', 'archive', old_uuid])

    with open(metadata) as file:
        data = file.readlines()
    date_str = data[1].split("[")[1].split("]")[0]
    date = datetime.strptime(date_str,"%d-%m-%Y %H:%M")
    created = date.strftime("%Y-%m-%dT%H:%M:%SZ")

    with rasterio.open(file_path) as dataset:
        crs = str(dataset.crs)
        transform = list(dataset.transform)
        
    uid = uuid.uuid4()

    
    geometry, lat_begin, lon_begin,  lat_end, lon_end = get_poly_coords(file_path, crs)

    docker_file_path = final_path + filename + ".tif"
    values = {
        'uid': uid,
        'crs': crs,
        'transform': transform,
        'created': created,
        'lat_begin' : lat_begin,
        'lon_begin' : lon_begin,
        'lat_end' : lat_end,
        'lon_end' : lon_end,
        'polygon_coords': geometry,
        'CWSI': CWSI_file_path,
        'ET': ET_file_path,
        'ETp': ETp_file_path,
        'WD': WD_file_path
    }
    
    filled_template = template.format(**values)
    with open(metadata_file, 'w') as f:
        f.write(filled_template)
    
    return metadata_file


def index_metadata(metadata_file: str) -> bool:
    import subprocess
   
    process = subprocess.Popen(['datacube', 'dataset', 'add', metadata_file, '-p', 'line3'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0: 
        raise Exception
    
def add_product(metadata_file: str) -> bool:
    import subprocess
   
    process = subprocess.Popen(['datacube', 'product', 'add', metadata_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0: 
        raise Exception
        
# %%
input_path = "./brunswick_20210817_TSEB_PT_20_ET_day_gf.tif"
metadata = "./bw_consignment_metadata.txt"
template_path =  "./product_template.yaml"
product_path =  "./product_metadata.yaml"

final_path = "/GeoData/l3/"
host = "localhost"
database = "odc_vicom"
user = "OpenDataCubeVicomtech"
password = "h97QAHRKPCdT7m7g"
port = "15432"

init = init_odc(host, database, user, password,port)

# %%
add_product(product_path)
# %%

metadata_file = generate_metadata(input_path, template_path, metadata,final_path)


# %%
index_metadata(metadata_file)
# %%

# %%

# %%
