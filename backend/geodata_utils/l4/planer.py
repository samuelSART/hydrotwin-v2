#%%


import pandas as pd
import random
import numpy as np
import requests

response = requests.get('http://localhost:5000/api/co2/get-agriculture-emissions?period=monthly')
uda_m = response.json()["data"]['emissions']
response = requests.get('http://localhost:5000/api/co2/get-agriculture-emissions?period=daily')
uda_d = response.json()["data"]['emissions']


response = requests.get('http://localhost:5000/api/co2/get-urban-emissions?period=monthly')
udu_m = response.json()["data"]['emissions']
response = requests.get('http://localhost:5000/api/co2/get-urban-emissions?period=daily')
udu_d = response.json()["data"]['emissions']

response = requests.get('http://localhost:5000/api/co2/get-industry-emissions?period=monthly')
udi_m = response.json()["data"]['emissions']
response = requests.get('http://localhost:5000/api/co2/get-industry-emissions?period=daily')
udi_d = response.json()["data"]['emissions']

response = requests.get('http://localhost:5000/api/co2/get-golf-emissions?period=monthly')
udg_m = response.json()["data"]['emissions']
response = requests.get('http://localhost:5000/api/co2/get-golf-emissions?period=daily')
udg_d = response.json()["data"]['emissions']


response = requests.get('http://localhost:5000/api/co2/get-wetland-emissions?period=monthly')
udw_m = response.json()["data"]['emissions']
response = requests.get('http://localhost:5000/api/co2/get-wetland-emissions?period=daily')
udw_d = response.json()["data"]['emissions']


# %%

ud = {

}


for values in [uda_d,udu_d,udi_d,udg_d,udw_d]:
    for value in values:
        id = value['code']
        ud[id] = {
            "daily":  value['demand'],
            "monthly": 0,
        }


for values in [uda_m,udu_m,udi_m,udg_m,udw_m]:
    for value in values:
        id = value['code']
        ud[id]['monthly'] = value['demand']

# %%
df = pd.DataFrame.from_dict(ud, orient='index')

df.to_csv("./CO2_emission.csv")

# %%


import pandas as pd
import random
import numpy as np
import requests

df = pd.read_csv("./last.csv")
emission = pd.read_csv("./CO2_emission.csv", index_col=0)
dates = df["date"].sort_values().unique()
demand = []
planned = []
co2 = []
superficial = []
subterranea = []
reutilizada = []
trasvase = []
desalada = []

for date in dates:
    aux_df = df[df['date'] == date]
    demand.append(int(aux_df["demand"].sum()))
    planned.append(int(aux_df["planned"].sum()))
    superficial = aux_df["planned"] * aux_df["superficial"]
    subterranea = aux_df["planned"] * aux_df["subterranea"]
    reutilizada = aux_df["planned"] * aux_df["reutilizada"]
    trasvase = aux_df["planned"] * aux_df["trasvase"]
    desalada = aux_df["planned"] * aux_df["desalada"]


#%%

output =  {
    "date": dates.tolist(),
    "demand": demand,
    "planned": planned,
    "subterranea": subterranea,
    "superficial": superficial,
    "reutilizada": reutilizada,
    "trasvase": trasvase,
    "desalada": desalada
}