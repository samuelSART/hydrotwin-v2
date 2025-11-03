import psycopg2
import psycopg2.extras as extras
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


def insert_control_point(conn, code, denomination, municipality, province, typology, description, x, y, EPSG):
    insert = ''' INSERT INTO public.control_point (code, denomination, municipality, province, typology, description, location) 
                 VALUES( %(code)s, %(denomination)s, %(municipality)s, %(province)s, %(typology)s, %(description)s, ST_SetSRID(ST_MakePoint(%(x)s,%(y)s), %(EPSG)s)) 
                 ON CONFLICT ON CONSTRAINT control_point_pkey
                 DO
                    UPDATE SET denomination = %(denomination)s, 
                                municipality = %(municipality)s, 
                                province = %(province)s, 
                                typology = %(typology)s, 
                                description = %(description)s,
                                location = ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), %(EPSG)s); '''
    cur = conn.cursor()
    parameters = {
        "code": code,
        "denomination": denomination,
        "municipality": municipality,
        "province": province,
        "typology": typology,
        "description": description,
        "x": x,
        "y": y,
        "EPSG": EPSG
    }
    cur.execute(insert, parameters)
    cur.close()
    conn.commit()


def insert_measurement_point(conn, code, control_point, denomination, typology, description, x, y, EPSG):
    insert = ''' INSERT INTO public.measurement_point (code, control_point, denomination, typology, description, location) 
                 VALUES(%(code)s, %(control_point)s, %(denomination)s, %(typology)s, %(description)s, ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), %(EPSG)s)) 
                 ON CONFLICT ON CONSTRAINT measurement_point_pkey
                 DO
                    UPDATE SET denomination = %(denomination)s, 
                                control_point = %(control_point)s,
                                typology = %(typology)s, 
                                description = %(description)s,
                                location = ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), %(EPSG)s); '''
    cur = conn.cursor()
    parameters = {
        "code": code,
        "denomination": denomination,
        "control_point": control_point,
        "typology": typology,
        "description": description,
        "x": x,
        "y": y,
        "EPSG": EPSG
    }
    try:
        cur.execute(insert, parameters)
    except psycopg2.errors.ForeignKeyViolation:
        cur.close()
        conn.rollback()
        cur = conn.cursor()
        parameters["control_point"] = None
        cur.execute(insert, parameters)
    cur.close()
    conn.commit()


def insert_variable(conn, code, measurement_point, typology, description):
    insert = ''' INSERT INTO public.variable (code, measurement_point, typology, description) 
                 VALUES(%(code)s, %(measurement_point)s, %(typology)s, %(description)s) 
                 ON CONFLICT ON CONSTRAINT variable_pkey
                 DO
                    UPDATE SET measurement_point = %(measurement_point)s, 
                                typology = %(typology)s, 
                                description = %(description)s; '''
    cur = conn.cursor()
    parameters = {
        "code": code,
        "measurement_point": measurement_point,
        "typology": typology,
        "description": description
    }
    try:
        cur.execute(insert, parameters)
    except psycopg2.errors.ForeignKeyViolation:
        cur.close()
        conn.rollback()
        cur = conn.cursor()
        parameters["measurement_point"] = None
        cur.execute(insert, parameters)
    cur.close()
    conn.commit()


def insert_demand_unit(conn, code, type, x, y, name, EPSG):
    insert = ''' INSERT INTO public.demand_unit (code, type, geometry, name)
                 VALUES(%(code)s, %(type)s, ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), %(EPSG)s), %(name)s)
                 ON CONFLICT ON CONSTRAINT demand_unit_pkey
                 DO
                    UPDATE SET type = %(type)s,
                                geometry = ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), %(EPSG)s),
                                name = %(name)s; '''

    cur = conn.cursor()
    parameters = {
        "code": code,
        "type": type,
        "x": x,
        "y": y,
        "name": name,
        "EPSG": EPSG
    }
    try:
        cur.execute(insert, parameters)
    except psycopg2.errors.ForeignKeyViolation:
        cur.close()
        conn.rollback()
        cur = conn.cursor()
        parameters["type"] = None
        cur.execute(insert, parameters)
    cur.close()
    conn.commit()


def insert_dataframe(conn, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]

    cols = ','.join(list(df.columns))

    query = 'INSERT INTO %s(%s) VALUES %%s' % (table, cols)
    cursor = conn.cursor()

    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()

    print("Records created successfully in table %s" % table)
    cursor.close()
