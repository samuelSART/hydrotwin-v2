
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

water_CO2 = {
    "superficial": 0.06,
    "subterranea": 0.9,
    "reutilizada": 0.78,
    "trasvase": 1.21,
    "desalada": 4.32
}
monthly = True
emission_column = "daily"
if monthly:
    emission_column = "monthly"
# %%

date = dates[0]


aux_df = df[df['date'] == date].set_index('id')
demand.append(int(aux_df["demand"].sum()))
planned.append(int(aux_df["planned"].sum()))

aux_df["superficial"] = aux_df["planned"] * aux_df["superficial"]
aux_df["total_CO2"] =  (aux_df["superficial"] * water_CO2["superficial"])

aux_df["subterranea"] = aux_df["planned"] * aux_df["subterranea"]
aux_df["total_CO2"] = aux_df["total_CO2"] +  (aux_df["subterranea"] * water_CO2["subterranea"])

aux_df["reutilizada"] = aux_df["planned"] * aux_df["reutilizada"]
aux_df["total_CO2"] = aux_df["total_CO2"] + (aux_df["reutilizada"] * water_CO2["reutilizada"])

aux_df["trasvase"] = aux_df["planned"] * aux_df["trasvase"]
aux_df["total_CO2"] = aux_df["total_CO2"] +( aux_df["trasvase"] * water_CO2["trasvase"])

aux_df["desalada"] = aux_df["planned"] * aux_df["desalada"]
aux_df["total_CO2"] = aux_df["total_CO2"] + (aux_df["desalada"] * water_CO2["desalada"])


aux_df = aux_df.merge(emission, how='left', left_index=True, right_index=True)
aux_df[emission_column] = aux_df[emission_column].fillna(0)
aux_df["co2"] = aux_df[emission_column] + aux_df["total_CO2"]

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