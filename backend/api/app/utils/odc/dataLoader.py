
import logging
import pandas as pd

from .polygonDataLoader import PolygonDataLoader


def process_polygon_data(loader, polygon, only_mean = False):
    return loader.load_polygon_data(polygon,  only_mean)


def is_multi_polygon(geometry):
    logging.debug(f'MultiPolygon geometry: {geometry.keys()}')
    return geometry['type'] == 'MultiPolygon'


def get_multi_polygon_list(geometry):
    return geometry['coordinates']


def load_polygon_data(  loader: PolygonDataLoader,
                        geometry_list: list,
                        only_mean: bool = False) -> pd.DataFrame:
    
    # Concat data
    loaded_polygon_data = []
    #num_cores = multiprocessing.cpu_count()
    # inputs = tqdm(multi_polygon_list)
    # loaded_polygon_data = Parallel(n_jobs=num_cores,  backend="threading")(delayed(process_polygon_data)(geometry, loader,only_mean))
    
    # TODO Check if it is a multipolygon
    for geometry in geometry_list:
        multi_polygon = is_multi_polygon(geometry)
        if not multi_polygon:
            logging.debug("Is not multipolygon")
            polygon = geometry["coordinates"]
            data = process_polygon_data(loader,polygon,only_mean)
            loaded_polygon_data.append(data)
        else:
            logging.debug("Is multipolygon")
            multi_polygon_list = get_multi_polygon_list(geometry)
            for polygon in multi_polygon_list:
                data = process_polygon_data((loader,polygon,only_mean))
                loaded_polygon_data.append(data)
    
    return pd.concat(loaded_polygon_data)

