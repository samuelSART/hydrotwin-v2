# Demand Unit CO2 emissions and removals
demand_unit_CO2 = {
    "agriculture": {  # t CO2 / ha-año
        "emissions": {
            "cereales_invierno": 1.754,
            "arroz": 4.856,
            "cereales_primavera": 1.37,
            "tuberculos": 4.2,
            "horticolas_protegido": 10.743,
            "horticolas_libre": 12.369,
            "citricos": 8.243,
            "frutales_fruto_carnoso": 6.862,
            "almendro": 12.03,
            "vinedo_vino": 1.8,
            "vinedo_mesa": 3,
            "olivar": 4.011,
            "sistema_riego": 1
        },
        "removals": {
            "cereales_invierno": -12.857,
            "arroz": -2.292,
            "cereales_primavera": -35.5,
            "tuberculos": -15.95,
            "horticolas_protegido": -28.369,
            "horticolas_libre": -15.91,
            "citricos": -25.56,
            "frutales_fruto_carnoso": -24.08,
            "almendro": -22.24,
            "vinedo_vino": -7.7,
            "vinedo_mesa": -20.7,
            "olivar": -16.7,
        }
    },
    "urban": {
        "emissions": 17.432137489428  # t CO2 / hm3
    },
    "industry": {
        "emissions": {  # t C02 / hm3
            "UDI01": 692074,
            "UDI02": 1211850,
            "UDI03": 372821,
            "UDI04": 478388,
            "UDI05": 799353,
            "UDI06": 386516,
            "UDI07": 168925,
        }
    },
    "golf": {
        "emissions": 692.67920511001  # t CO2 / hm3
    },
    "wetlands": {
        "removals": -395.2  # t CO2 / hm3
    }
}

# Distribution of water use
demand_water_distribution = {
    "superficial": 0.267751479289941,
    "subterranea": 0.329881656804734,
    "reutilizada": 0.144970414201183,
    "trasvase": 0.164201183431953,
    "desalada": 0.0931952662721894
}

# CO2 of each water origin type kW/hm3
water_CO2 = {
    "superficial": 60000,
    "subterranea": 900000,
    "reutilizada": 780000,
    "trasvase": 1210000,
    "desalada": 4320000
}

# t CO2 / kW
emission_factor = 0.000354


def calculate_agriculture_emissions(demands_crops, demands_water_df, period):
    emissions = []
    for demand_crops in demands_crops:
        demand_crops_emission = 0
        for key, value in demand_crops.items():
            if key in demand_unit_CO2["agriculture"]["emissions"]:
                if key != "demand_unit_code":
                    demand_crops_emission += (demand_unit_CO2["agriculture"]["emissions"][key] + demand_unit_CO2["agriculture"]
                                              ["emissions"]["sistema_riego"] + demand_unit_CO2["agriculture"]["removals"][key]) * value / period

        demand_water_emission = 0
        demand_water_df = demands_water_df[demands_water_df[
            'demand_unit_code'] == demand_crops['demand_unit_code']]
        if demand_water_df.shape[0] > 0:
            demand_water_emission = demand_water_df['flow'] * (demand_water_df['tipo_agua_superficial'] * water_CO2['superficial'] + demand_water_df['tipo_agua_subterranea'] * water_CO2['subterranea'] +
                                                               demand_water_df['tipo_agua_reutilizada'] * water_CO2['reutilizada'] + demand_water_df['tipo_agua_trasvase'] * water_CO2['trasvase'] + demand_water_df['tipo_agua_desalada'] * water_CO2['desalada']) * emission_factor
        emissions.append(
            {"code": demand_crops["demand_unit_code"], "total": demand_crops_emission + demand_water_emission.iloc[0], "demand": demand_crops_emission, "water": demand_water_emission.iloc[0]})
    return emissions


def calculate_urban_emissions(udu_simulation_df):
    udu_simulation_df['demand'] = udu_simulation_df.apply(
        lambda x: x['flow'] * demand_unit_CO2["urban"]["emissions"], axis=1)
    udu_simulation_df['water'] = udu_simulation_df.apply(lambda x: x['flow'] * (x['tipo_agua_superficial'] * water_CO2['superficial'] + x['tipo_agua_subterranea'] * water_CO2['subterranea'] +
                                                                                x['tipo_agua_reutilizada'] * water_CO2['reutilizada'] + x['tipo_agua_trasvase'] * water_CO2['trasvase'] + x['tipo_agua_desalada'] * water_CO2['desalada']) * emission_factor, axis=1)
    udu_simulation_df['total'] = udu_simulation_df.apply(
        lambda x: x['demand'] + x['water'], axis=1)

    return udu_simulation_df


def calculate_industry_emissions(udi_simulation_df):
    udi_simulation_df['demand'] = udi_simulation_df.apply(
        lambda x: x['flow'] * demand_unit_CO2["industry"]["emissions"][x['code']], axis=1)
    udi_simulation_df['water'] = udi_simulation_df.apply(lambda x: x['flow'] * (x['tipo_agua_superficial'] * water_CO2['superficial'] + x['tipo_agua_subterranea'] * water_CO2['subterranea'] +
                                                                                x['tipo_agua_reutilizada'] * water_CO2['reutilizada'] + x['tipo_agua_trasvase'] * water_CO2['trasvase'] + x['tipo_agua_desalada'] * water_CO2['desalada']) * emission_factor, axis=1)
    udi_simulation_df['total'] = udi_simulation_df.apply(
        lambda x: x['demand'] + x['water'], axis=1)

    return udi_simulation_df


def calculate_golf_emissions(udrg_simulation_df):
    udrg_simulation_df['demand'] = udrg_simulation_df.apply(
        lambda x: x['flow'] * demand_unit_CO2['golf']['emissions'], axis=1)
    udrg_simulation_df['water'] = udrg_simulation_df.apply(lambda x: x['flow'] * (x['tipo_agua_superficial'] * water_CO2['superficial'] + x['tipo_agua_subterranea'] * water_CO2['subterranea'] +
                                                                                  x['tipo_agua_reutilizada'] * water_CO2['reutilizada'] + x['tipo_agua_trasvase'] * water_CO2['trasvase'] + x['tipo_agua_desalada'] * water_CO2['desalada']) * emission_factor, axis=1)
    udrg_simulation_df['total'] = udrg_simulation_df.apply(
        lambda x: x['demand'] + x['water'], axis=1)

    return udrg_simulation_df


def calculate_wetland_emissions(wetland_simulation_df):
    wetland_simulation_df['demand'] = wetland_simulation_df.apply(
        lambda x: x['flow'] * demand_unit_CO2['wetlands']['removals'], axis=1)
    wetland_simulation_df['water'] = wetland_simulation_df.apply(lambda x: x['flow'] * (x['tipo_agua_superficial'] * water_CO2['superficial'] + x['tipo_agua_subterranea'] * water_CO2['subterranea'] +
                                                                                        x['tipo_agua_reutilizada'] * water_CO2['reutilizada'] + x['tipo_agua_trasvase'] * water_CO2['trasvase'] + x['tipo_agua_desalada'] * water_CO2['desalada']) * emission_factor, axis=1)
    wetland_simulation_df['total'] = wetland_simulation_df.apply(
        lambda x: x['demand'] + x['water'], axis=1)

    return wetland_simulation_df
