#!/usr/bin/env python
# coding: utf-8

############################
# CHS's Hydrological model #
############################


# Import libraries
import sys
import time
import pandas as pd
import numpy as np
from datetime import date, timedelta
import json
from operator import add
from flask import current_app


# Define constants

# CONFIG FILES AND THEIR SHEETS AND COLUMNS

# GENERIC CONFIG FILE
DATA_FOLDER = current_app.config['DATA_FOLDER']

CONFIG_FILE = DATA_FOLDER + 'L4/Model/CONFIG/CONFIG_FILE_tpl.tpa_dataframe_to_pywr.xlsx'
PHYSICAL_DATA_FILE = DATA_FOLDER + 'L4/Model/IN/OUT_SEGU.FIS_to_dataframe.xlsx'
RECURSOS_DEMANDAS_RESUMEN_DATA_FILE = DATA_FOLDER + \
    'L4/Model/IN/resumen_recursos_demandas_usos_PHDS1521.xlsx'

# SHEET and COLUMNS FOR physical_data_file, recursos_demandas_file

# PHYSICAL DATA FILE
CF_SHEET_IN_FILE_physical_data_file = 'IN_physical_data_file'
CFSIFpdf_HEADER = 0
CFSIFpdf_physical_data_file_path = 'IN_physical_data_file_path'
CFSIFpdf_sheet_datos_generales = 'sheet_datos_generales'
CFSIFpdf_header_general = 'header_general'

#####---------------------------------------#####
##### Sheets especiales y sus constantes    #####
#####---------------------------------------#####

CFSIFpdf_sheet_aportaciones = 'sheet_aportaciones'
CFSIFpdf_sheet_demandas = 'sheet_demandas'
CFSIFpdf_sheet_acuiferos = 'sheet_acuiferos'
CFSIFpdf_sheet_retornos = 'sheet_retornos'

#####---------------------------------------#####
##### Constantes para los sheets especiales #####
#####---------------------------------------#####

# ---APORTACIONES
CFSDA_col_nombre = 'nombre'
CFSDA_col_tipo_aportacion = 'tipo_aportacion'
CFSDA_col_nudo_destino = 'nudo_destino'
CFSDA_col_columna_en_archivo_aportaciones = 'columna_en_archivo_aportaciones'

# ---DEMANDAS
CFSDD_max_n_tomas = 5
CFSDD_col_nombre = 'nombre'
CFSDD_col_tipo_demanda_nombre = 'tipo_demanda_nombre'
CFSDD_col_demanda_mensual_12_vals = 'demanda_mensual_12_vals_Hm3'
CFSDD_col_coef_retorno = 'coef_retorno'
CFSDD_col_coef_consumo = 'coef_consumo'
CFSDD_col_n_elemento_retorno = 'n_elemento_retorno'

# ---ACUIFEROS
CFSDAC_col_n_acuif = 'n_acuif'
CFSDAC_col_nombre = 'nombre'
CFSDAC_col_tipo = 'tipo'
CFSDAC_col_volumen_inicial = 'volumen_inicial_Hm3'
CFSDAC_col_recarga_mensual_12_vals = 'recarga_mensual_12_vals_Hm3'

# ---RETORNOS
CFSDR_col_n_retorno = 'n_retorno'
CFSDR_col_nombre = 'nombre'
CFSDR_col_nudo_destino = 'nudo_destino'

# ARCHIVO DE RESUMEN DE DATOS ANUALES DE RECURSOS Y DEMANDAS

CF_SHEET_IN_FILE_recursos_demandas_file = 'IN_recursos_demandas_file'
CFSIFrdf_HEADER = 0
CFSIFrdf_header_general = 'header_general'
CFSIFrdf_header_recursos_clasificados = 'header_recursos_clasificados'

#####---------------------------------------#####
##### Sheets especiales y sus constantes    #####
#####---------------------------------------#####

CFSIFrdf_sheet_recursos = 'sheet_recursos'
CFSIFrdf_sheet_recursos_clasificados = 'sheet_recursos_clasificados'
CFSIFrdf_sheet_demandas = 'sheet_demandas'

#####---------------------------------------#####
##### Constantes para los sheets especiales #####
#####---------------------------------------#####

# ---RECURSOS
CFRDR_col_regimen_natural_superficiales = 'regimen_natural_superficiales'
CFRDR_col_regimen_natural_subterraneas = 'regimen_natural_subterraneas'
CFRDR_col_otras_subterraneas_BNOREs = 'otras_subterraneas_BNORE'
CFRDR_col_TTS_trasvase_tajo_segura = 'TTS_trasvase_tajo_segura'
CFRDR_col_TNA_trasvase_negratin_almanzora = 'TNA_trasvase_negratin_almanzora'
CFRDR_col_ACUAMED_aguilas_valdelentisco_torrevieja = 'ACUAMED_aguilas_valdelentisco_torrevieja'
CFRDR_col_MCT_san_pedro_alicante = 'MCT_san_pedro_alicante'
CFRDR_col_OTROS_escombreras_CARM_CCRR = 'OTROS_escombreras_CARM_CCRR'
CFRDR_col_OTROS_regenarada_o_directa = 'regenarada_o_directa'
CFRDR_col_OTROS_regenarada_indirecta = 'regenarada_indirecta'
CFRDR_col_OTROS_retornos_riego_azarbes = 'OTROS_retornos_riego_azarbes'
CFRDR_col_fugas = 'fugas'

# ---CLASIFICACION DE RECURSOS
CFRDR_col_superficial = 'superficial'
CFRDR_col_subterranea = 'subterranea'
CFRDR_col_trasvase = 'trasvase'
CFRDR_col_desalada = 'desalada'
CFRDR_col_reutilizada = 'reutilizada'
CFRDR_col_ficticia = 'ficticia'

CFRDR_col_superficial_percent = 'superficial_%'
CFRDR_col_subterranea_percent = 'subterranea_%'
CFRDR_col_trasvase_percent = 'trasvase_%'
CFRDR_col_desalada_percent = 'desalada_%'
CFRDR_col_reutilizada_percent = 'reutilizada_%'
CFRDR_col_ficticia_percent = 'ficticia_%'

# ---DEMANDAS
CFRDR_col_UDA = 'UDA'
CFRDR_col_UDU = 'UDU'
CFRDR_col_AMBIENTAL = 'AMBIENTAL'
CFRDR_col_UDI = 'UDI'
CFRDR_col_UDRG = 'UDRG'

N_MESES_YEAR_ESTANDAR = 12  # Generic constant
N_DIAS_MES_ESTANDAR = 30  # Generic constant
N_DIAS_YEAR_ESTANDAR = 366  # Generic constant

# DIRECTORIO DE SALIDA DE ARCHIVOS .csv DE APORTACIONES
PARAMETROS_APORTACIONES_DIRECTORIO_MENSUAL = DATA_FOLDER + \
    'L4/Model/PARAMETROS/APORTACIONES/MENSUAL/'
PARAMETROS_APORTACIONES_DIRECTORIO_DIARIO = DATA_FOLDER + \
    'L4/Model/PARAMETROS/APORTACIONES/DIARIO/'
PREFIJO_ARCHIVO_CSV_APORTACIONES_MENSUAL = 'APORTACION_M_'
PREFIJO_ARCHIVO_CSV_APORTACIONES_DIARIO = 'APORTACION_D_'
ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA = 'fecha'
ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR = 'valor'

# ------------------------- #

# Constantes de pasos de simulación
SIMULATION_STEP_PASO_DIARIO = 1
SIMULATION_STEP_PASO_MENSUAL = 2

# ------------------------- #

# Constantes genéricas
CAMPO_FECHA = 'fecha'
CAMPO_FECHA_YYYY_MM = 'fecha_yyyy_mm'
CAMPO_VALOR = 'valor'
MINIMUM_SIMULATION_DAYS = 15

# ------------------------- #

# Constantes para margen positivo y negativo a la hora de ajustar los valores anuales globes
MARGEN_DE_AJUSTE = 0.035

'''
Main code
'''


def getDemandResources():

    # 1. First, open config and input files

    # 1.1 Open CONFIG FILES file
    xl_cf = pd.ExcelFile(CONFIG_FILE)

    # 1.1.1 Get config data for file 'IN_physical_data_file'
    df_config_pdf = xl_cf.parse(
        sheet_name=CF_SHEET_IN_FILE_physical_data_file, header=CFSIFpdf_HEADER)

    # 1.1.2 Open IN_physical_data_file_path (phsycical data and elements' initialisation data file)
    xl_pdf = pd.ExcelFile(PHYSICAL_DATA_FILE)

    # Aportaciones
    df_pdf_aportaciones = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_aportaciones].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Demandas
    df_pdf_demandas = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_demandas].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Acuiferos
    df_pdf_acuiferos = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_acuiferos].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])
    # Retornos
    df_pdf_retornos = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_retornos].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Abrir archivo de resumen de recursos y demandas
    # 1.2.1 Get config data for file 'IN_recursos_demandas_file'
    df_config_rdf = xl_cf.parse(
        sheet_name=CF_SHEET_IN_FILE_recursos_demandas_file, header=CFSIFrdf_HEADER)

    # 1.2.2 Open file RECURSOS_DEMANDAS_RESUMEN_DATA_FILE
    xl_prf = pd.ExcelFile(RECURSOS_DEMANDAS_RESUMEN_DATA_FILE)

    # Recursos
    df_prf_recursos = xl_prf.parse(sheet_name=df_config_rdf[CFSIFrdf_sheet_recursos].iloc[0],
                                   header=df_config_rdf[CFSIFrdf_header_general].iloc[0])

    # Recursos clasificados
    df_prf_recursos_clasificados = xl_prf.parse(sheet_name=df_config_rdf[CFSIFrdf_sheet_recursos_clasificados].iloc[0],
                                                header=df_config_rdf[CFSIFrdf_header_recursos_clasificados].iloc[0])

    # Demandas
    df_prf_demandas = xl_prf.parse(sheet_name=df_config_rdf[CFSIFrdf_sheet_demandas].iloc[0],
                                   header=df_config_rdf[CFSIFrdf_header_general].iloc[0])

    # 2. Calcular los datos de las aportaciones (aguas superficiales, del trasvase y desaladas), acuíferos (aguas subterráneas)
    # y retornos (aguas reutilizadas). Trabajaremos con datos diarios para un año completo, y a partir de ahí sacaremos los datos
    # que nos interesan.
    # También, calculatr los datos de las demandas.

    # Primero, calculamos date_init_today (hoy), date_end_1_year (un año apartir de hoy) y date_end_simulation

    # date_init (hoy)
    date_init_today = date.today().strftime('%Y-%m-%d')

    # date_end_1_year (hoy más 1 año, 366 días)
    date_end_1_year = (pd.to_datetime(date_init_today) +
                       timedelta(days=N_DIAS_YEAR_ESTANDAR-1)).strftime('%Y-%m-%d')

    # date_end_simulation
    # IMPORTANTE: Se limita el tiempo máximo de simulación a (N_MESES_YEAR_ESTANDAR=12) x (N_DIAS_MES_ESTANDAR=30) días,
    # lo que equivale a 360 días de tiempo.
    # También, se limita el tiempo mìmimo de simulación a 15 dias (MINIMUM_SIMULATION_DAYS)
    simulation_days = N_MESES_YEAR_ESTANDAR * N_DIAS_MES_ESTANDAR
    date_end_simulation = (pd.to_datetime(
        date_init_today) + timedelta(days=simulation_days)).strftime('%Y-%m-%d')
    n_simulation_steps = (pd.to_datetime(
        date_end_simulation) - pd.to_datetime(date_init_today)).days + 1

    # IMPORTANTE: El tiempo mínimo de simulación deben ser 15 días (MINIMUM_SIMULATION_DAYS)
    if (n_simulation_steps < MINIMUM_SIMULATION_DAYS):
        date_end_simulation = (pd.to_datetime(date_init_today) +
                               timedelta(days=MINIMUM_SIMULATION_DAYS)).strftime('%Y-%m-%d')

        # Actualizamos n_simulation_steps
        n_simulation_steps = (pd.to_datetime(
            date_end_simulation) - pd.to_datetime(date_init_today)).days + 1

    # IMPORTANTE: Se limita el tiempo máximo de simulación a (N_MESES_YEAR_ESTANDAR=12) x (N_DIAS_MES_ESTANDAR=30) días,
    # lo que equivale a 360 días de tiempo.
    if (n_simulation_steps > (N_MESES_YEAR_ESTANDAR * N_DIAS_MES_ESTANDAR)):
        date_end_simulation = (pd.to_datetime(date_init_today) +
                               timedelta(days=(N_MESES_YEAR_ESTANDAR * N_DIAS_MES_ESTANDAR)-1)).strftime('%Y-%m-%d')

        # Actualizamos n_simulation_steps
        n_simulation_steps = (pd.to_datetime(
            date_end_simulation) - pd.to_datetime(date_init_today)).days + 1

    # También, calculamos el "day of year" de date_init_today, date_end_1_year y date_end_simulation
    date_init_today_day_of_year = pd.to_datetime(
        date_init_today).timetuple().tm_yday
    date_end_1_year_day_of_year = pd.to_datetime(
        date_end_1_year).timetuple().tm_yday
    date_end_simulation_day_of_year = pd.to_datetime(
        date_end_simulation).timetuple().tm_yday

    '''
    Calcular los datos de las aportaciones (preparamos datos diarios para un año completo, a partir de hoy)
    '''
    # Run for loop
    for i in range(df_pdf_aportaciones.shape[0]):
        # Determinamos el nombre de la aportación
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_aportacion = df_pdf_aportaciones[CFSDA_col_nombre].iloc[i].replace(
            '"', '')

        # Determinamos el tipo de la aportación
        tipo_aportacion = df_pdf_aportaciones[CFSDA_col_tipo_aportacion].iloc[i]

        # Determinamos la columna en el archivo de aportaciones
        columna_en_archivo_aportaciones = df_pdf_aportaciones[
            CFSDA_col_columna_en_archivo_aportaciones].iloc[i]

        # Creamos los datos de aportaciones con los archivos de datos diarios

        # DATOS DIARIOS
        # Determinamos el nombre del archivo de aportaciones diarias, abrimos el archivo y obtenemos los datos que nos interesan:
        # Nombre de archivo
        file_name_aportaciones = PARAMETROS_APORTACIONES_DIRECTORIO_DIARIO + \
            PREFIJO_ARCHIVO_CSV_APORTACIONES_DIARIO + \
            str(columna_en_archivo_aportaciones) + '.csv'

        # Abrir archivo para obtener todos los datos
        df_values_aportacion_diario_all = pd.read_csv(file_name_aportaciones)

        # Obtener los datos del periodo de interés (1 año desde hoy)
        df_values_aportacion_diario_1_year = \
            df_values_aportacion_diario_all[df_values_aportacion_diario_all[
                ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA] >= date_init_today]
        df_values_aportacion_diario_1_year = \
            df_values_aportacion_diario_1_year[df_values_aportacion_diario_1_year[
                ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA] <= date_end_1_year]

        # Tenemos los campos ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR y ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA (equivalentes
        # a los campos genéricos CAMO_VALOR y CAMPO_FECHA). Añadimos otros campos de interés
        # Nombre
        df_values_aportacion_diario_1_year[CFSDA_col_nombre] = nombre_aportacion
        # Tipo
        df_values_aportacion_diario_1_year[CFSDA_col_tipo_aportacion] = tipo_aportacion

        # Actualizar el df con la info de todas las aportaciones diarias
        if (i == 0):
            df_datos_aportaciones_diario_1_year = df_values_aportacion_diario_1_year.copy()
        else:
            df_datos_aportaciones_diario_1_year = pd.concat([df_datos_aportaciones_diario_1_year,
                                                             df_values_aportacion_diario_1_year.copy()], ignore_index=True)

    # También creamos el campo CAMPO_FECHA_YYYY_MM, para poder ordenar los datos fácilmente por meses
    df_datos_aportaciones_diario_1_year[CAMPO_FECHA_YYYY_MM] = \
        pd.to_datetime(
            df_datos_aportaciones_diario_1_year[ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA]).dt.strftime('%Y-%m')

    # Reorder columns
    columnas = [ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA,
                CAMPO_FECHA_YYYY_MM,
                ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR,
                CFSDA_col_nombre,
                CFSDA_col_tipo_aportacion]

    # Aplicar las columnas ordenadas
    df_datos_aportaciones_diario_1_year = df_datos_aportaciones_diario_1_year[columnas]
    df_datos_aportaciones_diario_1_year.reset_index(drop=True, inplace=True)

    # IMPORTANTE: ahora que tenemos las aportaciones anuales por tipo de aportacion, ajustamos los valores
    # a los valores de lo que son los valores anuales habituales, que vienen del archivo de resumen de datos
    # de recursos y demandas "resumen_recursos_demandas_usos_PHDS1521.xlsx"
    # Lo que haremso aquí es calcular los factores multiplicadores a aplicar a la hora de crear los Inputs en el modelo.

    dic_factores_multiplicadores_aportaciones = {}

    #----------------'superficial'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_cantidad_agua_superficial_1_year_DE_PARTIDA = \
        df_datos_aportaciones_diario_1_year[df_datos_aportaciones_diario_1_year[CFSDA_col_tipo_aportacion] ==
                                            CFRDR_col_superficial][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_recursos_clasificados[CFRDR_col_superficial].values[0] / \
        g_cantidad_agua_superficial_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_aportaciones[CFRDR_col_superficial] = factor_multiplicador_de_ajuste

    #----------------'trasvase'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_cantidad_agua_trasvase_1_year_DE_PARTIDA = \
        df_datos_aportaciones_diario_1_year[df_datos_aportaciones_diario_1_year[CFSDA_col_tipo_aportacion] ==
                                            CFRDR_col_trasvase][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_recursos_clasificados[CFRDR_col_trasvase].values[0] / \
        g_cantidad_agua_trasvase_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_aportaciones[CFRDR_col_trasvase] = factor_multiplicador_de_ajuste

    #----------------'desalada'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_cantidad_agua_desalada_1_year_DE_PARTIDA = \
        df_datos_aportaciones_diario_1_year[df_datos_aportaciones_diario_1_year[CFSDA_col_tipo_aportacion] ==
                                            CFRDR_col_desalada][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # Creamos un df filtrado por 'desalada'
    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_recursos_clasificados[CFRDR_col_desalada].values[0] / \
        g_cantidad_agua_desalada_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_aportaciones[CFRDR_col_desalada] = factor_multiplicador_de_ajuste

    '''
    Calcular los datos de las demandas (trabajamos con datos diarios).
    De partida, tenemos datos para un año completo.
    '''

    # Run for loop
    for i in range(df_pdf_demandas.shape[0]):
        # Determinamos el nombre de la demanda
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_demanda = df_pdf_demandas[CFSDD_col_nombre].iloc[i].replace(
            '"', '')

        # Determinamos el tipo de la demanda
        tipo_demanda = df_pdf_demandas[CFSDD_col_tipo_demanda_nombre].iloc[i]

        # Empezamos con los parámetros de caudal de demanda mensual para demandas:
        values_str_mensual = df_pdf_demandas[CFSDD_col_demanda_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]

        # Pasamos a calcular los datos diarios:
        # A total of 366 values must be provided."
        # Lo que haremos es lo siguiente:
        # + Para los meses impares, generaremos 31 valores.
        # + Para los meses pares, generaremos 30 valores
        for j in range(len(values_list_mensual)):
            if (((j+1) % 2) == 1):
                valores_diarios_temp = [values_list_mensual[j]/31] * 31
            else:
                valores_diarios_temp = [values_list_mensual[j]/30] * 30
            if (j == 0):
                values_list_diario = valores_diarios_temp
            else:
                # Concatena la segunda lista a la primera
                values_list_diario = values_list_diario + valores_diarios_temp

        # Creamos un dataframe con los datos diarios de 1 año
        df_values_demanda_diario_1_to_366 = pd.DataFrame(
            values_list_diario, columns=[CAMPO_VALOR])

        # IMPORTANTE: como estamos definiendo 366 días, date_end_1_year_day_of_year siempre será >= date_init_today_day_of_year.
        # Por tanto, los datos siempre hay que tomarlos en 2 tramos.
        df_values_demanda_diario_1_year = \
            pd.concat([df_values_demanda_diario_1_to_366.iloc[(date_init_today_day_of_year-1):N_DIAS_YEAR_ESTANDAR, :].copy(),
                       df_values_demanda_diario_1_to_366.iloc[0:date_end_1_year_day_of_year-1, :].copy()], axis=0, ignore_index=True)

        # Tenemos el campo CAMPO_VALOR, añadimos otros campos de interés.
        # Para crear la fecha, convertimos el índice en un campo (que se llamará 'index')
        df_values_demanda_diario_1_year.reset_index(inplace=True)

        # Ahora, creamos la fecha
        df_values_demanda_diario_1_year[CAMPO_FECHA] = \
            df_values_demanda_diario_1_year['index'].apply(lambda x: pd.to_datetime(
                (pd.to_datetime(date_init_today) + timedelta(days=x)).strftime('%Y-%m-%d')))

        # Eliminamos el campo temporal 'index'
        df_values_demanda_diario_1_year.drop(columns=['index'], inplace=True)

        # Resto de campos de interés
        # Nombre
        df_values_demanda_diario_1_year[CFSDD_col_nombre] = nombre_demanda
        # Tipo
        df_values_demanda_diario_1_year[CFSDD_col_tipo_demanda_nombre] = tipo_demanda

        # Actualizar el df con la info de todas las demandas mensuales
        if (i == 0):
            df_datos_demandas_diario_1_year = df_values_demanda_diario_1_year.copy()
        else:
            df_datos_demandas_diario_1_year = pd.concat([df_datos_demandas_diario_1_year,
                                                         df_values_demanda_diario_1_year.copy()], ignore_index=True)

    # También creamos el campo CAMPO_FECHA_YYYY_MM, para poder ordenar los datos fácilmente por meses
    df_datos_demandas_diario_1_year[CAMPO_FECHA_YYYY_MM] = \
        df_datos_demandas_diario_1_year[CAMPO_FECHA].dt.strftime('%Y-%m')

    # Reorder columns
    columnas = [CAMPO_FECHA,
                CAMPO_FECHA_YYYY_MM,
                CAMPO_VALOR,
                CFSDD_col_nombre,
                CFSDD_col_tipo_demanda_nombre]

    # Aplicar las columnas ordenadas
    df_datos_demandas_diario_1_year = df_datos_demandas_diario_1_year[columnas]
    df_datos_demandas_diario_1_year.reset_index(drop=True, inplace=True)

    # IMPORTANTE: ahora que tenemos las aportaciones anuales por tipo de aportacion, ajustamos los valores
    # a los valores de lo que son los valores anuales habituales, que vienen del archivo de resumen de datos
    # de recursos y demandas "resumen_recursos_demandas_usos_PHDS1521.xlsx"
    # Lo que haremso aquí es calcular los factores multiplicadores a aplicar a la hora de crear los Inputs en el modelo.

    dic_factores_multiplicadores_demandas = {}

    #----------------'UDAs'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_demanda_UDAs_1_year_DE_PARTIDA = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_tipo_demanda_nombre] ==
                                        CFRDR_col_UDA][CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_demandas[CFRDR_col_UDA].values[0] / \
        g_demanda_UDAs_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_demandas[CFRDR_col_UDA] = factor_multiplicador_de_ajuste

    #----------------'UDUs'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_demanda_UDUs_1_year_DE_PARTIDA = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_tipo_demanda_nombre] ==
                                        CFRDR_col_UDU][CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_demandas[CFRDR_col_UDU].values[0] / \
        g_demanda_UDUs_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_demandas[CFRDR_col_UDU] = factor_multiplicador_de_ajuste

    #----------------'UDIs'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_demanda_UDIs_1_year_DE_PARTIDA = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_tipo_demanda_nombre] ==
                                        CFRDR_col_UDI][CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_demandas[CFRDR_col_UDI].values[0] / \
        g_demanda_UDIs_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_demandas[CFRDR_col_UDI] = factor_multiplicador_de_ajuste

    #----------------'AMBIENTAL'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_demanda_AMBIENTAL_1_year_DE_PARTIDA = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_tipo_demanda_nombre] ==
                                        CFRDR_col_AMBIENTAL][CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_demandas[CFRDR_col_AMBIENTAL].values[0] / \
        g_demanda_AMBIENTAL_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_demandas[CFRDR_col_AMBIENTAL] = factor_multiplicador_de_ajuste

    #----------------'UDRG'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_demanda_UDRGs_1_year_DE_PARTIDA = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_tipo_demanda_nombre] ==
                                        CFRDR_col_UDRG][CAMPO_VALOR].sum()

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_demandas[CFRDR_col_UDRG].values[0] / \
        g_demanda_UDRGs_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_demandas[CFRDR_col_UDRG] = factor_multiplicador_de_ajuste

    '''
    Calcular los datos de los retornos (trabajamos con datos diarios).
    De partida, tenemos datos para un año completo.
    '''

    # Run for loop
    for i in range(df_pdf_retornos.shape[0]):
        # A continuación, comprobar si es un destino de alguna toma de demanda.
        # IMPORTANTE:
        # Es posible que el retorno sea destino de tomas de N demandas; cada demanda puede tener varias tomas,
        # pero, por cada demanda, hay que contabilizar q_max una sola vez, porque aunque la demanda tenga varias tomas,
        # todas entran en la misma demanda y la q_max de la demanda es única; además, todas esas tomas tienen los mismos valores
        # para fraccion_demanda y fraccion_retorno.
        #
        # Sin embargo, lo que SI hay que tener en cuenta es que el retorno puede ser destino de tomas de N demandas y, por tanto,
        # a la hora de contabilizar el q_max del retorno, hay que tener en cuenta todas las demandas

        # Determinamos el nombre del retorno y e número de retorno
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_retorno = df_pdf_retornos[CFSDR_col_nombre].iloc[i].replace(
            '"', '')
        n_retorno = df_pdf_retornos[CFSDR_col_n_retorno].iloc[i]

        # Determinamos las demandas que alimentan dichos retornos
        df_demandas_a_considerar = \
            df_pdf_demandas[(df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(1)] == n_retorno) |
                            (df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(2)] == n_retorno) |
                            (df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(3)] == n_retorno) |
                            (df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(4)] == n_retorno) |
                            (df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(5)] == n_retorno)]

        # Hacemos la suma de las demandas (teniendo en cuenta su fraccion de retorno)
        # Inicialización
        # Inicializar values_list_diario con (N_DIAS_YEAR_ESTANDAR = 366) valores de 0.0
        values_list_diario = [0.0] * N_DIAS_YEAR_ESTANDAR

        # Empezamos con la suma
        for j in range(df_demandas_a_considerar.shape[0]):
            # Actualizamos values_list_mensual y values_list_diario.
            # Primero, determinamos el nombre de la demanda correspondiente.
            # NOTA: al nombre del elemento, le quitamos las comillas.
            demanda = df_demandas_a_considerar[CFSDD_col_nombre].iloc[j].replace(
                '"', '')

            # Valores diarios
            values_list_diario = list(map(add, values_list_diario,
                                          df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_nombre] == demanda][CAMPO_VALOR].values *
                                          df_demandas_a_considerar[CFSDD_col_coef_retorno + '_' + str(1)].values[0]))

        # Ahora, crear los parámetros, si procede
        if (df_demandas_a_considerar.shape[0] > 0):

            # Creamos un dataframe con los datos diarios de 1 año
            df_values_retorno_diario_1_to_366 = pd.DataFrame(
                values_list_diario, columns=[CAMPO_VALOR])

            # IMPORTANTE: como estamos definiendo 366 días, date_end_1_year_day_of_year siempre será >= date_init_today_day_of_year.
            # Por tanto, los datos siempre hay que tomarlos en 2 tramos.
            df_values_retorno_diario_1_year = \
                pd.concat([df_values_retorno_diario_1_to_366.iloc[(date_init_today_day_of_year-1):N_DIAS_YEAR_ESTANDAR, :].copy(),
                           df_values_retorno_diario_1_to_366.iloc[0:date_end_1_year_day_of_year-1, :].copy()], axis=0, ignore_index=True)

            # Tenemos el campo CAMPO_VALOR, añadimos otros campos de interés.
            # Para crear la fecha, convertimos el índice en un campo (que se llamará 'index')
            df_values_retorno_diario_1_year.reset_index(inplace=True)

            # Ahora, creamos la fecha
            df_values_retorno_diario_1_year[CAMPO_FECHA] = \
                df_values_retorno_diario_1_year['index'].apply(lambda x: pd.to_datetime(
                    (pd.to_datetime(date_init_today) + timedelta(days=x)).strftime('%Y-%m-%d')))

            # Eliminamos el campo temporal 'index'
            df_values_retorno_diario_1_year.drop(
                columns=['index'], inplace=True)

            # Resto de campos de interés
            # Nombre
            df_values_retorno_diario_1_year[CFSDR_col_nombre] = nombre_retorno

            # Actualizar el df con la info de todas las retornos mensuales
            if (i == 0):
                df_datos_retornos_diario_1_year = df_values_retorno_diario_1_year.copy()
            else:
                df_datos_retornos_diario_1_year = pd.concat([df_datos_retornos_diario_1_year,
                                                             df_values_retorno_diario_1_year.copy()], ignore_index=True)

    # También creamos el campo CAMPO_FECHA_YYYY_MM, para poder ordenar los datos fácilmente por meses
    df_datos_retornos_diario_1_year[CAMPO_FECHA_YYYY_MM] = \
        df_datos_retornos_diario_1_year[CAMPO_FECHA].dt.strftime('%Y-%m')

    # Reorder columns
    columnas = [CAMPO_FECHA,
                CAMPO_FECHA_YYYY_MM,
                CAMPO_VALOR,
                CFSDR_col_nombre]

    # Aplicar las columnas ordenadas
    df_datos_retornos_diario_1_year = df_datos_retornos_diario_1_year[columnas]
    df_datos_retornos_diario_1_year.reset_index(drop=True, inplace=True)

    # IMPORTANTE: ahora que tenemos las aportaciones anuales por tipo de aportacion, ajustamos los valores
    # a los valores de lo que son los valores anuales habituales, que vienen del archivo de resumen de datos
    # de recursos y demandas "resumen_recursos_demandas_usos_PHDS1521.xlsx"
    # Lo que haremso aquí es calcular los factores multiplicadores a aplicar a la hora de crear los Inputs en el modelo.

    #----------------'reutilizada'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_cantidad_agua_reutilizada_1_year_DE_PARTIDA = df_datos_retornos_diario_1_year[CAMPO_VALOR].sum(
    )

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_recursos_clasificados[CFRDR_col_reutilizada].values[0] / \
        g_cantidad_agua_reutilizada_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_aportaciones[CFRDR_col_reutilizada] = factor_multiplicador_de_ajuste

    '''
    Calcular los datos de las acuiferos (trabajamos con datos diarios).
    De partida, tenemos datos para un año completo.
    '''

    # Run for loop
    for i in range(df_pdf_acuiferos.shape[0]):
        # Determinamos el nombre de la acuifero
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_acuifero = df_pdf_acuiferos[CFSDAC_col_nombre].iloc[i].replace(
            '"', '')

        values_str_mensual = df_pdf_acuiferos[CFSDAC_col_recarga_mensual_12_vals].iloc[i]

        # Empezamos con los parámetros de caudal de acuifero mensual para acuiferos:
        values_str_mensual = df_pdf_acuiferos[CFSDAC_col_recarga_mensual_12_vals].iloc[i]
        # Hay casos en los que no se define la recarga, por tanto,
        if (values_str_mensual != values_str_mensual):
            # hay que considerarlo (NOTA: esta forma de hacer el if() es una forma
            # de saber si un valor es NaN.
            # Creamos un una lista de [0.0] 12 veces
            values_list_mensual = [0.0] * 12
        else:
            values_list_mensual = [float(j)
                                   for j in values_str_mensual.split()]

        # Pasamos a calcular los datos diarios:
        # A total of 366 values must be provided."
        # Lo que haremos es lo siguiente:
        # + Para los meses impares, generaremos 31 valores.
        # + Para los meses pares, generaremos 30 valores
        for j in range(len(values_list_mensual)):
            if (((j+1) % 2) == 1):
                valores_diarios_temp = [values_list_mensual[j]/31] * 31
            else:
                valores_diarios_temp = [values_list_mensual[j]/30] * 30
            if (j == 0):
                values_list_diario = valores_diarios_temp
            else:
                # Concatena la segunda lista a la primera
                values_list_diario = values_list_diario + valores_diarios_temp

        # Creamos un dataframe con los datos diarios de 1 año
        df_values_acuifero_diario_1_to_366 = pd.DataFrame(
            values_list_diario, columns=[CAMPO_VALOR])

        # IMPORTANTE: como estamos definiendo 366 días, date_end_1_year_day_of_year siempre será >= date_init_today_day_of_year.
        # Por tanto, los datos siempre hay que tomarlos en 2 tramos.
        df_values_acuifero_diario_1_year = \
            pd.concat([df_values_acuifero_diario_1_to_366.iloc[(date_init_today_day_of_year-1):N_DIAS_YEAR_ESTANDAR, :].copy(),
                       df_values_acuifero_diario_1_to_366.iloc[0:date_end_1_year_day_of_year-1, :].copy()], axis=0, ignore_index=True)

        # Tenemos el campo CAMPO_VALOR, añadimos otros campos de interés.
        # Para crear la fecha, convertimos el índice en un campo (que se llamará 'index')
        df_values_acuifero_diario_1_year.reset_index(inplace=True)

        # Ahora, creamos la fecha
        df_values_acuifero_diario_1_year[CAMPO_FECHA] = \
            df_values_acuifero_diario_1_year['index'].apply(lambda x: pd.to_datetime(
                (pd.to_datetime(date_init_today) + timedelta(days=x)).strftime('%Y-%m-%d')))

        # Eliminamos el campo temporal 'index'
        df_values_acuifero_diario_1_year.drop(columns=['index'], inplace=True)

        # Resto de campos de interés
        # Nombre
        df_values_acuifero_diario_1_year[CFSDAC_col_nombre] = nombre_acuifero

        # Actualizar el df con la info de todas las acuiferos mensuales
        if (i == 0):
            df_datos_acuiferos_diario_1_year = df_values_acuifero_diario_1_year.copy()
        else:
            df_datos_acuiferos_diario_1_year = pd.concat([df_datos_acuiferos_diario_1_year,
                                                          df_values_acuifero_diario_1_year.copy()], ignore_index=True)

    # También creamos el campo CAMPO_FECHA_YYYY_MM, para poder ordenar los datos fácilmente por meses
    df_datos_acuiferos_diario_1_year[CAMPO_FECHA_YYYY_MM] = \
        df_datos_acuiferos_diario_1_year[CAMPO_FECHA].dt.strftime('%Y-%m')

    # Reorder columns
    columnas = [CAMPO_FECHA,
                CAMPO_FECHA_YYYY_MM,
                CAMPO_VALOR,
                CFSDAC_col_nombre]

    # Aplicar las columnas ordenadas
    df_datos_acuiferos_diario_1_year = df_datos_acuiferos_diario_1_year[columnas]
    df_datos_acuiferos_diario_1_year.reset_index(drop=True, inplace=True)

    #----------------'subterranea'-------------------#

    # Primero, obtenemos los valores globales de los datos actuales
    g_cantidad_agua_subterranea_1_year_DE_PARTIDA = df_datos_acuiferos_diario_1_year[CAMPO_VALOR].sum(
    )

    # Calculamos el factor multiplicador de ajuste
    factor_multiplicador_de_ajuste = df_prf_recursos_clasificados[CFRDR_col_subterranea].values[0] / \
        g_cantidad_agua_subterranea_1_year_DE_PARTIDA

    # Guardamos el factor multiplicador en el dicccionario
    dic_factores_multiplicadores_aportaciones[CFRDR_col_subterranea] = factor_multiplicador_de_ajuste

    # Preparamos los datos a devolver: APORTACIONES

    # Aportación de agua 'superficial'
    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_cantidad_agua_superficial_1_year_DISPONIBLE = g_cantidad_agua_superficial_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_aportaciones[CFRDR_col_superficial] * \
        factor_multiplicador_mas_menos

    # Aportación de agua 'trasvase'
    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_cantidad_agua_trasvase_1_year_DISPONIBLE = g_cantidad_agua_trasvase_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_aportaciones[CFRDR_col_trasvase] * \
        factor_multiplicador_mas_menos

    # Aportación de agua 'desalada'
    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_cantidad_agua_desalada_1_year_DISPONIBLE = g_cantidad_agua_desalada_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_aportaciones[CFRDR_col_desalada] * \
        factor_multiplicador_mas_menos

    # Aportación de agua 'subterranea'
    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_cantidad_agua_subterranea_1_year_DISPONIBLE = g_cantidad_agua_subterranea_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_aportaciones[CFRDR_col_subterranea] * \
        factor_multiplicador_mas_menos

    # Aportación de agua 'reutilizada'
    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_cantidad_agua_reutilizada_1_year_DISPONIBLE = g_cantidad_agua_reutilizada_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_aportaciones[CFRDR_col_reutilizada] * \
        factor_multiplicador_mas_menos

    # Preparamos los datos a devolver: DEMANDAS

    #----------------'UDAs'-------------------#

    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_demanda_UDAs_1_year_PREVISTO = g_demanda_UDAs_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_demandas[CFRDR_col_UDA] * \
        factor_multiplicador_mas_menos

    #----------------'UDUs'-------------------#

    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_demanda_UDUs_1_year_PREVISTO = g_demanda_UDUs_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_demandas[CFRDR_col_UDU] * \
        factor_multiplicador_mas_menos

    #----------------'UDIs'-------------------#

    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_demanda_UDIs_1_year_PREVISTO = g_demanda_UDIs_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_demandas[CFRDR_col_UDI] * \
        factor_multiplicador_mas_menos

    #----------------'AMBIENTALs'-------------------#

    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_demanda_AMBIENTAL_1_year_PREVISTO = g_demanda_AMBIENTAL_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_demandas[CFRDR_col_AMBIENTAL] * \
        factor_multiplicador_mas_menos

    #----------------'UDRGs'-------------------#

    np.random.seed()
    factor_multiplicador_mas_menos = \
        np.random.uniform(low=(1-MARGEN_DE_AJUSTE),
                          high=(1+MARGEN_DE_AJUSTE), size=1)[0]

    # Ajustamos los valores
    g_demanda_UDRGs_1_year_PREVISTO = g_demanda_UDRGs_1_year_DE_PARTIDA * \
        dic_factores_multiplicadores_demandas[CFRDR_col_UDRG] * \
        factor_multiplicador_mas_menos

    # Resultados devueltos

    # 1. json con datos de aportaciones
    # Primero, creamos un dataframe
    data_results_aportaciones_1_year = {CFRDR_col_superficial: [g_cantidad_agua_superficial_1_year_DISPONIBLE],
                                        CFRDR_col_subterranea: [g_cantidad_agua_subterranea_1_year_DISPONIBLE],
                                        CFRDR_col_trasvase: [g_cantidad_agua_trasvase_1_year_DISPONIBLE],
                                        CFRDR_col_desalada: [g_cantidad_agua_desalada_1_year_DISPONIBLE],
                                        CFRDR_col_reutilizada: [g_cantidad_agua_reutilizada_1_year_DISPONIBLE]}

    df_results_aportaciones_1_year = pd.DataFrame(
        data=data_results_aportaciones_1_year)

    # Guardarlo en una variable a devolver
    json_aportaciones_1_year = df_results_aportaciones_1_year.to_json(
        orient='records')

    # 2. json con datos de demandas
    data_results_demandas_1_year = {CFRDR_col_UDA: [g_demanda_UDAs_1_year_PREVISTO],
                                    CFRDR_col_UDU: [g_demanda_UDUs_1_year_PREVISTO],
                                    CFRDR_col_AMBIENTAL: [g_demanda_AMBIENTAL_1_year_PREVISTO],
                                    CFRDR_col_UDI: [g_demanda_UDIs_1_year_PREVISTO],
                                    CFRDR_col_UDRG: [g_demanda_UDRGs_1_year_PREVISTO]}

    df_results_demandas_1_year = pd.DataFrame(
        data=data_results_demandas_1_year)

    # Guardarlo en una variable a devolver
    json_demandas_1_year = df_results_demandas_1_year.to_json(orient='records')

    # Devolvemos
    return {'availableResources': json.loads(json_aportaciones_1_year)[0], 'demandResources': json.loads(json_demandas_1_year)[0]}
