#%% 


import database_utils as db
from shapely.geometry import shape
# %%

conn = db.connect()
uds = db.select_uds(conn)
bodys = db.select_origins(conn)

# %%
def myTouches(poly1, poly2):
    return poly1.intersects(poly2) and not poly1.crosses(poly2) and not poly1.contains(poly2)

connexion = {

}
for ud in uds:
    code_ud = ud[0]
    geometry_ud = ud[3]
    polygon_ud = shape(geometry_ud)
    water_list = []
    for body in bodys:
        code_water = body[0]
        geometry_water = body[3]
        polygon_water = shape(geometry_water)
        if myTouches(polygon_ud.buffer(0), polygon_water.buffer(0)):
            water_list.append(code_water)
    connexion[code_ud] = water_list
# %%
def insert_demand_water_relation(conn, water_body, demand_unit):
    insert = ''' INSERT INTO public.demand_water_relation (water_body, demand_unit) 
                 VALUES(%s, %s)
                 ON CONFLICT ON CONSTRAINT demand_water_relation_pkey
                 DO NOTHING; '''
    cur = conn.cursor()
    cur.execute(insert, (water_body, demand_unit,))
    cur.close()
    conn.commit()

# %%
conn = db.connect()
for demand_code in connexion:
    water_list = connexion[demand_code]
    for water_code in water_list:
        if "." not in water_code:
            insert_demand_water_relation(conn, water_code, demand_code)
        

# %%
import pandas as pd
superficial_relation = {

}

underground = []
relations_underground = pd.read_excel("./aquifer_subterranean.xls", header=None)
relations_superf = pd.read_excel("./msup.xlsx", header=None, names=["Origin","Target"])

 
relations_underground = pd.read_excel(pd.ExcelFile("./aquifer_subterranean.xls"), 'RD por acuífero',header=None)


for _,row in relations_superf.iterrows():
    if type(row["Target"]) == str: 
        if row["Target"] != "Null":
            superficial_relation[row["Origin"]] = row["Target"].split(",")


# %%
for _,row in relations_underground.iloc[5:].iterrows():
    try:
        subterranean_code = row[0]
        aquifer_code = str(row[2])
        if int(aquifer_code) < 100:
            aquifer_code = "0"+ aquifer_code
        if int(aquifer_code) < 10:
            aquifer_code = "0"+ aquifer_code
        underground.append([subterranean_code, aquifer_code])
    except:
        continue


def insert_water_relation(conn, water_body_1, water_body_2):
    insert = ''' INSERT INTO public.water_body_relation (water_body_1, water_body_2) 
                 VALUES(%s, %s)
                 ON CONFLICT ON CONSTRAINT water_body_relation_pkey
                 DO NOTHING; '''
    cur = conn.cursor()
    cur.execute(insert, (water_body_1, water_body_2,))
    cur.close()
    conn.commit()
# %%
conn = db.connect()
for water_code_1 in superficial_relation:
    water_list = superficial_relation[water_code_1]
    for water_code_2 in water_list:
        insert_water_relation(conn, water_code_1, water_code_2)

# %%
conn = db.connect()
for relation in underground:
    
    insert_water_relation(conn, relation[0], relation[1])

# %%
