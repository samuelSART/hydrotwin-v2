import psycopg2
from decouple import config

USER = config('POSTGRES_USER', default='admin')
PASS = config('POSTGRES_PASSWORD', default='4dm1n_p4ss')
DB = config('POSTGRES_DB', default='hydrotwin')
HOST = config('POSTGRES_HOST', default='localhost')
PORT = config('POSTGRES_PORT', default=5432)



def connect():
    return psycopg2.connect(dbname=DB,
                            user=USER, 
                            password=PASS,
                            host=HOST,
                            port=PORT)
    

def insert_ud_polygon(conn, code, type, geom, epsg, name):
    insert = ''' INSERT INTO public.demand_unit (code,type,geometry,name) 
                 VALUES(%(code)s, %(type)s, ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), (%(epsg)s)), %(name)s) 
                 ON CONFLICT ON CONSTRAINT demand_units_pkey
                 DO
                    UPDATE SET geometry = ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), (%(epsg)s)); '''
    cur = conn.cursor()
    params = {
        "code": code,
        "type": type,
        "geom": geom,
        "epsg": epsg,
        "name": name
    }
    cur.execute(insert, params)
    cur.close()
    conn.commit()

def insert_superficial_polygon(conn, code, type, EUMSPFCOD, name, category, geom, epsg):
    insert = ''' INSERT INTO public.water_body (code,type,name,category,geometry)
                 VALUES (%(code)s,%(type)s,%(name)s,%(category)s, ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), (%(epsg)s))); 
                 INSERT INTO public.superficial(code, eumspfcod) 
                 VALUES(%(code)s, %(eumspfcod)s);
                 '''
    cur = conn.cursor()
    params = {
        "code": code,
        "type": type,
        "geom": geom,
        "epsg": epsg,
        "name": name,
        "eumspfcod" : EUMSPFCOD
    }
    cur.execute(insert, params)
    cur.close()
    conn.commit()

def insert_superficial_polygon(conn, code, type, EUMSPFCOD, name, category, geom, epsg):
    insert = ''' INSERT INTO public.water_body (code,type,name,category,geometry)
                 VALUES (%(code)s,%(type)s,%(name)s,%(category)s, ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), (%(epsg)s))); 
                 INSERT INTO public.superficial(code, eumspfcod) 
                 VALUES(%(code)s, %(eumspfcod)s);
                 '''
    cur = conn.cursor()
    params = {
        "code": code,
        "type": type,
        "category": category,
        "geom": geom,
        "epsg": epsg,
        "name": name,
        "eumspfcod" : EUMSPFCOD
    }
    cur.execute(insert, params)
    cur.close()
    conn.commit()



def insert_underground_polygon(conn, code, type, EUMSBTCOD, name, category, geom, epsg):
    insert = ''' 
                INSERT INTO public.water_body (code,type,name,category,geometry)
                VALUES (%(code)s,%(type)s,%(name)s,%(category)s, ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), (%(epsg)s))); 
                INSERT INTO public.underground (code, EUMSBTCOD) 
                 VALUES(%(code)s, %(EUMSBTCOD)s); '''
    cur = conn.cursor()
    params = {
        "code": code,
        "type": type,
        "geom": geom,
        "category": category,
        "epsg": epsg,
        "name": name,
        "EUMSBTCOD" : EUMSBTCOD
    }
    cur.execute(insert,params)
    cur.close()
    conn.commit()

def insert_aquifer_polygon(conn, code, type, superpos, name, category, geom, epsg):
    insert = ''' 
                INSERT INTO public.water_body (code,type,name,category,geometry)
                VALUES (%(code)s,%(type)s,%(name)s,%(category)s, ST_SetSRID(ST_GeomFromGeoJSON(%(geom)s), (%(epsg)s))); 
                INSERT INTO public.aquifer (code, superposition) 
                 VALUES(%(code)s, %(superpos)s); '''
    cur = conn.cursor()
    params = {
        "code": code,
        "type": type,
        "geom": geom,
        "category": category,
        "epsg": epsg,
        "name": name,
        "superpos" : superpos
    }
    cur.execute(insert,params)
    cur.close()
    conn.commit()


def select_uds(conn, epsg="EPSG:4326"):
    insert = ''' SELECT code,name,type, ST_AsGeoJSON( ST_Transform(geometry, %s))::JSON AS geometry 
                FROM public.demand_units; '''
    cur = conn.cursor()
    cur.execute(insert, (epsg,))
    data = cur.fetchall()
    cur.close()
    return data



def select_origins(conn, epsg="EPSG:4326"):
    insert = ''' SELECT code,name,type, ST_AsGeoJSON( ST_Transform(geometry, %s))::JSON AS geometry 
                FROM public.water_body; '''
    cur = conn.cursor()
    cur.execute(insert, (epsg,))
    data = cur.fetchall()
    cur.close()
    return data