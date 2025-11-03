# BANDS #
wrf_bands = {
    "T2": [],
    "PSFC": [],
    "U10": [],
    "V10": [],
    "SFCEVP": [],
    "QSFC": [],
    "SWDOWN": [],
    "TACC_PRECIP": [],
}

wrf_monthly_bands = {
    "d2m": [],
    "e": [],
    "msl": [],
    "ssrd": [],
    "t2m": [],
    "tp": [],
    "u10": [],
    "v10": [],
}

evapotranspiration_bands = {
    "ET": [],
}

waterdemand_bands = {
    "WD": [],
}

biomass_bands = {
    "BM": [],
}

irrigation_bands = {
    "IR": [],
}
irrigation_advice_bands = {
    "IR_AD": [],
}

irrigation_prob_bands = {
    "IRp": [],
}

crop_type_bands = {
    "CT": [],
}

water_content_bands = {
    "VWC": []
}

exchange_bands = {
    "R": []
}

recharge_bands = {
    "PR": []
}

infiltration_bands = {
    "IN": []
}


# STYLES #
style_evapotranspiration_ET = {
    "name": "ET",
    "title": "Evapotranspiration",
    "abstract": " Evapotranspiration",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "ET"
        }
    },
    "needed_bands": ["ET"],
    "range": [0.0, 10.0],
    "mpl_ramp": "winter",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0.0",
        "end": "10.0",
        "ticks_every": "1",
        "title": "Evapotranspiración",
        "units": "mm/dia",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_evapotranspiration_ET_monthly = {
    "name": "ET_monthly",
    "title": "Evapotranspiration",
    "abstract": " Evapotranspiration",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "ET"
        }
    },
    "needed_bands": ["ET"],
    "range": [0.0, 300.0],
    "mpl_ramp": "winter",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0.0",
        "end": "300.0",
        "ticks_every": "50",
        "title": "Evapotranspiración",
        "units": "mm/mes",
        "decimal_places": 0,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_waterdemand = {
    "name": "WD",
    "title": "Water Demand",
    "abstract": " Water Demand",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "WD"
        }
    },
    "needed_bands": ["WD"],
    "range": [0, 6],
    "mpl_ramp": "summer",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "6",
        "ticks_every": "1",
        "title": "Demanda de agua",
        "units": "mm",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_waterdemand_monthly = {
    "name": "WD_monthly",
    "title": "Water Demand",
    "abstract": " Water Demand",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "WD"
        }
    },
    "needed_bands": ["WD"],
    "range": [0, 300],
    "mpl_ramp": "summer",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "300",
        "ticks_every": "50",
        "title": "Demanda de agua",
        "units": "mm",
        "decimal_places": 0,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_irrigation_advice = {
    "name": "IR_AD",
    "title": "Irrigation advice",
    "abstract": "Irrigation advice",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "IR_AD"
        }
    },
    "needed_bands": ["IR_AD"],
    "color_ramp": [{
        "value": 0,
        "color": "white",
        "alpha": 1.0
    }, {
        "value": 1,
        "color": "green",
        "alpha": 1.0
    },
        {
        "value": 2,
        "color": "orange",
        "alpha": 1.0
    }, {
        "value": 3,
        "color": "red",
        "alpha": 1.0
    }
    ],

    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "3",
        "ticks_every": "1",
        "title": "Propuesta de riego",
        "units": "",
        "tick_labels": {
            "0": {"label": "No dato"},
            "1": {"label": "No-necesaria"},
            "2": {"label": "Necesaria"},
            "3": {"label": "Critica"},
        },
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_irrigation = {
    "name": "IR",
    "title": "Irrigation info",
    "abstract": "Irrigation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "IR"
        }
    },
    "needed_bands": ["IR"],
    "color_ramp": [{
        "value": 0,
        "color": "#FF5733",
        "alpha": 1.0
    },
        {
            "value": 1,
            "color": "#99ff33",
            "alpha": 1.0
    }],

    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "1",
        "ticks_every": "1",
        "title": "Irrigado?",
        "units": "",
        "tick_labels": {
            "0": {"label": "No"},
            "1": {"label": "Si"},
        },
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_biomass = {
    "name": "BM",
    "title": "Biomass production",
    "abstract": "Historical biomass production ",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "BM"
        }
    },
    "needed_bands": ["BM"],
    "range": [0, 1000],
    "mpl_ramp": "summer",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0.0",
        "end": "1000",
        "ticks_every": "100",
        "title": "Biomasa producida",
        "units": "g/m2",
        "decimal_places": 0,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_crop_type = {
    "name": "CT",
    "title": "Crop classification",
    "abstract": "Historical crop classification",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "CT"
        }
    },
    "needed_bands": ["CT"],
    "color_ramp": [{
        "value": 1,
        "color": "#05612C",
        "alpha": 1.0
    }, {
        "value": 2,
        "color": "#C01F3D",
        "alpha": 1.0
    },
        {
        "value": 3,
            "color": "#C4B310",
            "alpha": 1.0
    }, {
        "value": 4,
            "color": "#4E1CB3",
            "alpha": 1.0
    }, {
        "value": 5,
            "color": "#524F59",
            "alpha": 1.0
    }, {
        "value": 6,
            "color": "#EEEBF5",
            "alpha": 1.0
    }],

    "legend": {
        "show_legend": True,
        "begin": "1",
        "end": "6",
        "ticks_every": "1",
        "title": "Tipo de cultivo",
        "units": "",
        "tick_labels": {
            "1": {"label": "LAC"},
            "2": {"label": "LBC"},
            "3": {"label": "V"},
            "4": {"label": "H"},
            "5": {"label": "INV"},
            "6": {"label": "NaN"},
        },
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

# WRF
style_predict_TACC_PRECIP = {
    "name": "TACC_PRECIP",
    "title": "Total Accumulated Precipitation",
    "abstract": "Total Accumulated Precipitation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "TACC_PRECIP"
        }

    },
    "needed_bands": ["TACC_PRECIP"],
    "range": [0, 25],
    "mpl_ramp": "winter",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "25",
        "ticks_every": "5",
        "title": "RAINC + RAINNC + RAINSHV (Liq. Eqiv.)",
        "units": "mm",
        "decimal_places": 1,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_SWDOWN = {
    "name": "SWDOWN",
    "title": "Downward short wave flux",
    "abstract": "Downward short wave flux at ground surface",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "SWDOWN"
        }
    },
    "needed_bands": ["SWDOWN"],
    "range": [0, 250],
    "mpl_ramp": "hot",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "250",
        "ticks_every": "25",
        "title": "Flujo de onda corta",
        "units": "W m-2",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_QSFC = {
    "name": "QSFC",
    "title": "Specific humidity",
    "abstract": "Specific humidity at lower boundary",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "QSFC"
        }
    },
    "needed_bands": ["QSFC"],
    "range": [0, 0.2],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "0.2",
        "ticks_every": "0.05",
        "title": "Humedad especifica en el limite inferior", 
        "units": "kg kg-1",
        "decimal_places": 4,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_SFCEVP = {
    "name": "SFCEVP",
    "title": "Accumulated surface evaporation",
    "abstract": "Accumulated surface evaporation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "SFCEVP"
        }
    },
    "needed_bands": ["SFCEVP"],
    "range": [0, 2000],
    "mpl_ramp": "winter",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "2000",
        "ticks_every": "250",
        "title": "Evaporación superficial acumulada",
        "units": "W m-2",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_PSFC = {
    "name": "PSFC",
    "title": "Surface Pressure",
    "abstract": "Surface Pressure",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "PSFC"
        }
    },
    "needed_bands": ["PSFC"],
    "range": [75000, 104000],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "75000",
        "end": "104000",
        "ticks_every": "5000",
        "title": "Presión superficial",
        "units": "Pa",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_T2 = {
    "name": "T2",
    "title": "Temperature",
    "abstract": " Temperature at 2 Meters",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "T2"
        }
    },
    "needed_bands": ["T2"],
    "range": [253, 323],
    "mpl_ramp": "cool",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "253",
        "end": "323",
        "ticks_every": "10",
        "title": "Temperature a 2m",
        "units": "K",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

# WRF MONTHLY
style_predict_tp = {
    "name": "tp",
    "title": "Total Accumulated Precipitation",
    "abstract": "Total Accumulated Precipitation ",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "tp"
        }
    },
    "needed_bands": ["tp"],
    "range": [0, 25],
    "mpl_ramp": "winter",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "25",
        "ticks_every": "5",
        "title": "RAINC + RAINNC + RAINSHV (Liq. Eqiv.)",
        "units": "mm",
        "decimal_places": 1,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_ssrd = {
    "name": "ssrd",
    "title": "Surface solar radiation downwards",
    "abstract": "Surface solar radiation downwards at ground surface",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "ssrd"
        }
    },
    "needed_bands": ["ssrd"],
    "range": [0, 29179904],
    "mpl_ramp": "Wistia",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "29179904",
        "ticks_every": "5000000",
        "title": "Radiación solar superficial",
        "units": "J m**-2",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_d2m = {
    "name": "d2m",
    "title": "2 metre dewpoint temperature",
    "abstract": "2 metre dewpoint temperature",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "d2m"
        }
    },
    "needed_bands": ["d2m"],
    "range": [253, 323],
    "mpl_ramp": "cool",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "253",
        "end": "323",
        "ticks_every": "10",
        "title": "Temperatura del punto de rocío a 2m",
        "units": "K",
        "decimal_places": 4,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_e = {
    "name": "e",
    "title": "Accumulated surface evaporation",
    "abstract": "Accumulated surface evaporation",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "e"
        }
    },
    "needed_bands": ["e"],
    "range": [-0.8, -0.1],
    "mpl_ramp": "winter",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "-0.8",
        "end": "-0.1",
        "ticks_every": "0.2",
        "title": "Evaporación superficial acumulada",
        "units": "m",
        "decimal_places": 1,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_msl = {
    "name": "msl",
    "title": "Mean sea level pressure",
    "abstract": "Mean sea level pressure",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "msl"
        }
    },
    "needed_bands": ["msl"],
    "range": [75000, 104000],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "75000",
        "end": "104000",
        "ticks_every": "5000",
        "title": "Presión media a nivel del mar",
        "units": "Pa",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_predict_t2m = {
    "name": "t2m",
    "title": "Temperature at 2 Meters",
    "abstract": " Temperature at 2 Meters",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "t2m"
        }
    },
    "needed_bands": ["t2m"],
    "range": [253, 323],
    "mpl_ramp": "cool",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "253",
        "end": "323",
        "ticks_every": "10",
        "title": "Temperatura del punto de rocío a 2m",
        "units": "K",
        "decimal_places": 4,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

# LINE 2
style_recharge = {
    "name": "PR",
    "title": "Precipitation rate",
    "abstract": "Precipitation rate",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "PR"
        }
    },
    "needed_bands": ["PR"],
    "range": [-30, 450],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "-30",
        "end": "450",
        "ticks_every": "50",
        "title": "Tasa de precipitación",
        "units": "mm/dia",
        "decimal_places": 4,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_infiltration = {
    "name": "IN",
    "title": "Infiltration",
    "abstract": "Infiltration",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "IN"
        }
    },
    "needed_bands": ["IN"],
    "range": [-21, 0],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "-21",
        "end": "0",
        "ticks_every": "4",
        "title": "Infiltración",
        "units": "mm/dia",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_exchange = {
    "name": "R",
    "title": "Recharge",
    "abstract": "Recharge",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "R"
        }
    },
    "needed_bands": ["R"],
    "range": [-30, 30],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "-30",
        "end": "30",
        "ticks_every": "10",
        "title": "Recarga",
        "units": "mm/dia",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}

style_water_content = {
    "name": "VWC",
    "title": "Volumetric water content",
    "abstract": "Volumetric water content",
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "VWC"
        }
    },
    "needed_bands": ["VWC"],
    "range": [0, 0.5],
    "mpl_ramp": "viridis",
    "include_in_feature_info": True,
    "legend": {
        "show_legend": True,
        "begin": "0",
        "end": "0.5",
        "ticks_every": "0.1",
        "title": "Contenido volumétrico de agua",
        "units": "",
        "decimal_places": 2,
        "rcParams": {
            "lines.linewidth": 2,
            "font.weight": "bold",
            "xtick.labelsize": 6,
            "grid.alpha": 0,
            "legend.framealpha": 0
        },
        "width": 4,
        "height": 1.25
    }
}


# REUSABLE CONFIG FRAGMENTS - resource limit declarations
standard_resource_limits = {
    "wms": {
        "zoomed_out_fill_colour": [150, 180, 200, 160],
        "min_zoom_factor": 200.0,
        "max_datasets": 25,
        "min_zoom_level": 7,
        "dataset_cache_rules": [
            # Where number of datasets less than the min_datasets element of the first cache rule  (0-3 in this example):
            #       no-cache.
            {
                "min_datasets": 4,
                "max_age": 86400,  # 86400 seconds = 24 hours
            },
            {
                "min_datasets": 8,
                "max_age": 604800,  # 604800 seconds = 1 week
            },
        ]
    },
    "wcs": {
        "max_datasets": 25,
    }
}


# MAIN CONFIGURATION OBJECT
ows_cfg = {
    # Config entries in the "global" section apply to all services and all layers/coverages
    "global": {
        "response_headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "services": {
            "wms": True,
            "wmts": True,
            "wcs": True
        },
        "title": "Open web-services for HydroTwin",
        "allowed_urls": ["http://localhost:8000/",
                         "http://ows:8000/"],
        "info_url": "http://opendatacube.org",
        "abstract": """This web-service serves georectified raster data from the Confederación Hidrográfica del Segura.""",
        "keywords": [
            "satellite",
            "time-series",
            "CHS",
        ],
        "contact_info": {},
        "attribution": {
            # Attribution must contain at least one of ("title", "url" and "logo")
            # A human readable title for the attribution - e.g. the name of the attributed organisation
            "title": "Confederación Hidrográfica del Segura",
            # The associated - e.g. URL for the attributed organisation
            "url": "https://www.chsegura.es",
            # Logo image - e.g. for the attributed organisation
            "logo": {
                # Image width in pixels (optional)
                "width": 400,
                # Image height in pixels (optional)
                "height": 400,
                # URL for the logo image. (required if logo specified)
                "url": "https://pbs.twimg.com/profile_images/1053407255276777473/KSW3-Pim.jpg",
                # Image MIME type for the logo - should match type referenced in the logo url (required if logo specified.)
                "format": "image/jpg",
            }
        },
        # If fees are charged for the use of the service, these can be described here in free text.
        # If blank or not included, defaults to "none".
        "fees": "",
        # If there are constraints on access to the service, they can be described here in free text.
        # If blank or not included, defaults to "none".
        "access_constraints": "",
        # Supported co-ordinate reference systems. Any coordinate system supported by GDAL and Proj.4J can be used.
        # At least one CRS must be included.  At least one geographic CRS must be included if WCS is active.
        # WGS-84 (EPSG:4326) is strongly recommended, but not required.
        # Web Mercator (EPSG:3857) is strongly recommended, but is only required if WMTS is active.
        "published_CRSs": {
            "EPSG:3857": {  # Web Mercator
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:4326": {  # WGS-84
                "geographic": True,
                "vertical_coord_first": True
            },
            "EPSG:25830": {  # WGS-84
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:3111": {  # VicGrid94 for delwp.vic.gov.au
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:3577": {  # GDA-94, internal representation
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:32630": {
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            }
        },
    },  # End of "global" section.

    # Config items in the "wms" section apply to the WMS service (and WMTS, which is implemented as a
    # thin wrapper to the WMS code unless stated otherwise) to all WMS/WMTS layers (unless over-ridden).
    "wms": {
        "max_width": 256,
        "max_height": 256,
        "authorities": {
            # The authorities dictionary maps names to authority urls.
            "auth": "https://authoritative-authority.com",
            "idsrus": "https://www.identifiers-r-us.com",
        }
    },  # End of "wms" section.

    "wmts": {
        "tile_matrix_sets": {
            "vicgrid": {
                # The CRS of the Tile Matrix Set
                "crs": "EPSG:3111",
                # The coordinates (in the CRS above) of the upper-left
                # corner of the tile matrix set.
                "matrix_origin": (1786000.0, 3081000.0),
                # The size of tiles (must not exceed the WMS maximum tile size)
                "tile_size": (256, 256),
                # The scale denominators (as defined in the WMTS spec) for
                # the various zoom level from right out, to zoomed right in.
                "scale_set": [
                    7559538.928601667,
                    3779769.4643008336,
                    1889884.7321504168,
                    944942.3660752084,
                    472471.1830376042,
                    236235.5915188021,
                    94494.23660752083,
                    47247.11830376041,
                    23623.559151880207,
                    9449.423660752083,
                    4724.711830376042,
                    2362.355915188021,
                    1181.1779575940104,
                    755.9538928601667,
                ],
                "matrix_exponent_initial_offsets": (1, 0),
            },
        }
    },

    # Config items in the "wcs" section apply to the WCS service to all WCS coverages
    # (unless over-ridden).
    "wcs": {
        "formats": {
            # Key is the format name, as used in DescribeCoverage XML
            "GeoTIFF": {
                # Writing your own renderers is not documented.
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_tiff",
                    "2": "datacube_ows.wcs2_utils.get_tiff",
                },
                # The MIME type of the image, as used in the Http Response.
                "mime": "image/geotiff",
                # The file extension to add to the filename.
                "extension": "tif",
                # Whether or not the file format supports multiple time slices.
                "multi-time": False
            },
            "NetCDF": {
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_netcdf",
                    "2": "datacube_ows.wcs2_utils.get_netcdf",
                },
                "mime": "application/x-netcdf",
                "extension": "nc",
                "multi-time": True,
            }
        },
        "native_format": "GeoTIFF",
    },  # End of "wcs" section

    "layers": [
        {
            # NOTE: This layer is a folder - it is NOT "named layer" that can be selected in GetMap requests
            "title": "Line-3",
            "abstract": "Products containing data ultimately derived from line 3.",
            "keywords": [
                "line3",
            ],
            "layers": [
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Evapotranspiration (short term)",
                    "queryable": True,
                    "abstract": "Short term actual evapotranspiration forecast ",
                    "name": "evapotranspiration",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "evapotranspiration",
                    "bands": evapotranspiration_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "ET",
                        "styles": [
                            style_evapotranspiration_ET]
                    },
                    "keywords": [
                        "ET",
                        "evapotranspiration",
                        "short term"
                    ]
                },  # End of sentinel2_nrt multi-product definition,
                {   # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Evapotranspiration (long term)",
                    "queryable": True,
                    "abstract": "Long term actual evapotranspiration forecast ",
                    "name": "evapotranspiration_monthly",
                    "multi_product": False,
                    "time_resolution": "month",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "evapotranspiration_monthly",
                    "bands": evapotranspiration_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "ET_monthly",
                        "styles": [
                            style_evapotranspiration_ET_monthly]
                    },
                    "keywords": [
                        "ET",
                        "evapotranspiration",
                        "long term"
                    ]
                },  # End of sentinel2_nrt multi-product definition,
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Water deficit (short term)",
                    "queryable": True,
                    "abstract": "Short term water deficit forecast",
                    "name": "waterdemand",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "waterdemand",
                    "bands": waterdemand_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "WD",
                        "styles": [
                            style_waterdemand]
                    },
                    "keywords": [
                        "water",
                        "deficit",
                        "short term"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Water deficit (long term)",
                    "queryable": True,
                    "abstract": "Long term actual water deficit forecast ",
                    "name": "waterdemand_monthly",
                    "multi_product": False,
                    "time_resolution": "month",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "waterdemand_monthly",
                    "bands": waterdemand_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "WD_monthly",
                        "styles": [
                            style_waterdemand_monthly]
                    },
                    "keywords": [
                        "water",
                        "deficit",
                        "long term"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Historical biomass production",
                    "queryable": True,
                    "abstract": "Historical biomass production",
                    "name": "biomass",
                    "multi_product": False,
                    "time_resolution": "month",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "biomass",
                    "bands": biomass_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "BM",
                        "styles": [
                            style_biomass]
                    },
                    "keywords": [
                        "historical",
                        "biomass",
                        "production"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Irrigation advice",
                    "queryable": True,
                    "abstract": "Irrigation advice",
                    "name": "irrigation_advice",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "irrigation_advice",
                    "bands": irrigation_advice_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "IR_AD",
                        "styles": [
                            style_irrigation_advice]
                    },
                    "keywords": [
                        "historical",
                        "irrigation_advice"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Historical irrigated",
                    "queryable": True,
                    "abstract": "Historical irrigated are mapping",
                    "name": "irrigation",
                    "multi_product": False,
                    "time_resolution": "month",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "irrigation",
                    "bands": irrigation_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "IR",
                        "styles": [
                            style_irrigation]
                    },
                    "keywords": [
                        "historical",
                        "irrigation"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Historical crop classification",
                    "queryable": True,
                    "abstract": "Historical crop classification",
                    "name": "crop_type",
                    "multi_product": False,
                    "time_resolution": "month",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "crop_type",
                    "bands": crop_type_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.00186171000000, 0.00186171000000],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "CT",
                        "styles": [
                            style_crop_type]
                    },
                    "keywords": [
                        "historical",
                        "crop"
                    ]
                },
            ],
        },  # End of Sentinel-2 folder
        {
            # NOTE: This layer is a folder - it is NOT "named layer" that can be selected in GetMap requests
            "title": "Line-2",
            "abstract": "Products containing data ultimately derived from line 2.",
            "keywords": [
                "line2",
            ],
            "layers": [
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Average water content in the rootzone",
                    "queryable": True,
                    "abstract": "Average water content in the rootzone",
                    "name": "water_content",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "water_content",
                    "bands": water_content_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:25830",
                    "native_resolution": [500, -500],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "VWC",
                        "styles": [
                            style_water_content]
                    },
                    "keywords": [
                        "average",
                        "water",
                        "content",
                        "rootzone"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Total recharge to SZ (pos.down)",
                    "queryable": True,
                    "abstract": "Total recharge to SZ (pos.down)",
                    "name": "recharge",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "recharge",
                    "bands": recharge_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:25830",
                    "native_resolution": [500, -500],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "PR",
                        "styles": [
                            style_recharge]
                    },
                    "keywords": [
                        "total",
                        "recharge",
                        "SZ"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Exchange between UZ and SZ (pos.up)",
                    "queryable": True,
                    "abstract": "Exchange between UZ and SZ (pos.up)",
                    "name": "exchange",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "exchange",
                    "bands": exchange_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:25830",
                    "native_resolution": [500, -500],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "R",
                        "styles": [
                            style_exchange]
                    },
                    "keywords": [
                        "exchange",
                        "UZ",
                        "SZ"
                    ]
                },
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Infiltration to UZ (negative)",
                    "queryable": True,
                    "abstract": " Infiltration to UZ (negative)",
                    "name": "infiltration",
                    "multi_product": False,
                    "time_resolution": "day",
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "infiltration",
                    "bands": infiltration_bands,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:25830",
                    "native_resolution": [500, -500],
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "IN",
                        "styles": [
                            style_infiltration]
                    },
                    "keywords": [
                        "infiltration",
                        "UZ"
                    ]
                },
            ],
        },
        {
            # NOTE: This layer is a folder - it is NOT "named layer" that can be selected in GetMap requests
            "title": "Line-1",
            "abstract": "Products containing data ultimately derived from line 1.",
            "keywords": [
                "line1",
            ],
            "layers": [
                {
                    "title": "Weather Forecast Product",
                    "queryable": True,
                    "abstract": "Predict from the model WRF",
                    "name": "wrf_daily",
                    "multi_product": False,
                    "product_name": "wrf_daily",
                    "bands": wrf_bands,
                    "resource_limits": standard_resource_limits,
                    "dynamic": True,
                    "time_resolution": "day",
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.03125, 0.03125],
                    "wcs": {
                        "native_format": "GeoTIFF"
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "TACC_PRECIP",
                        "styles": [
                            style_predict_TACC_PRECIP,
                            style_predict_T2,
                            style_predict_PSFC,
                            style_predict_QSFC,
                            style_predict_SFCEVP,
                            style_predict_SWDOWN
                        ]
                    },
                    "keywords": [
                        "weather",
                        "forecast"
                    ]
                },
                {
                    "title": "Weather Forecast Product Monthly",
                    "queryable": True,
                    "abstract": "Predict from the model WRF Monthly",
                    "name": "wrf_monthly",
                    "multi_product": False,
                    "product_name": "wrf_monthly",
                    "bands": wrf_monthly_bands,
                    "resource_limits": standard_resource_limits,
                    "dynamic": True,
                    "time_resolution": "day",
                    "native_crs": "EPSG:4326",
                    "native_resolution": [-0.03125, 0.03125],
                    "wcs": {
                        "native_format": "GeoTIFF"
                    },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    "styling": {
                        "default_style": "tp",
                        "styles": [
                            style_predict_tp,
                            style_predict_t2m,
                            style_predict_e,
                            style_predict_d2m,
                            style_predict_msl,
                            style_predict_ssrd
                        ]
                    },
                    "keywords": [
                        "weather",
                        "forecast",
                        "monthly"
                    ]
                }
            ],
        },
    ]
}
