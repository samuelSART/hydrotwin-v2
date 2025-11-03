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

#----------------------------------------------------------#
# Seguimos con el resto de sheets del archivo principal    #
#----------------------------------------------------------#

# RECURSOS_DEMANDAS FILE
CF_SHEET_IN_FILE_recursos_demandas_file = 'IN_recursos_demandas_file'
CFSIFrdf_HEADER = 0
CFSIFrdf_physical_data_file_path = 'IN_recursos_demandas_file_path'
CFSIFrdf_col_sheet_recursos = 'sheet_recursos'
CFSIFrdf_col_sheet_demandas = 'sheet_demandas'
CFSIFrdf_col_header_general = 'header_general'

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


'''
Main code
'''


def getResources():

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

    # 2. Calcular los datos de las aportaciones (aguas superficiales, del trasvase y desaladas), acuíferos (aguas subterráneas)
    # y retornos (aguas reutilizadas). Trabajaremos con datos diarios para un año completo, y a partir de ahí sacaremos los datos
    # que nos interesan.

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
    simulation_days = np.random.uniform(low=10, high=400, size=1)[0]
    date_end_simulation = (pd.to_datetime(
        date_init_today) + timedelta(days=simulation_days)).strftime('%Y-%m-%d')
    n_simulation_steps = (pd.to_datetime(
        date_end_simulation) - pd.to_datetime(date_init_today)).days + 1

    # IMPORTANTE: El tiempo mínimo de simulación deben ser 15 días (MINIMUM_SIMULATION_DAYS)
    if (n_simulation_steps < MINIMUM_SIMULATION_DAYS):
        date_end_simulation = (pd.to_datetime(
            date_init_today) + timedelta(days=MINIMUM_SIMULATION_DAYS)).strftime('%Y-%m-%d')

        # Actualizamos n_simulation_steps
        n_simulation_steps = (pd.to_datetime(
            date_end_simulation) - pd.to_datetime(date_init_today)).days + 1

    # IMPORTANTE: Se limita el tiempo máximo de simulación a (N_MESES_YEAR_ESTANDAR=12) x (N_DIAS_MES_ESTANDAR=30) días,
    # lo que equivale a 360 días de tiempo.
    if (n_simulation_steps > (N_MESES_YEAR_ESTANDAR * N_DIAS_MES_ESTANDAR)):
        date_end_simulation = (pd.to_datetime(date_init_today) + timedelta(
            days=(N_MESES_YEAR_ESTANDAR * N_DIAS_MES_ESTANDAR)-1)).strftime('%Y-%m-%d')

        # Actualizamos n_simulation_steps
        n_simulation_steps = (pd.to_datetime(
            date_end_simulation) - pd.to_datetime(date_init_today)).days + 1

    # También, calculamos el "day of year" de date_init_today, date_end_1_year y date_end_simulation
    date_init_today_day_of_year = pd.to_datetime(
        date_init_today).timetuple().tm_yday
    date_end_1_year_day_of_year = pd.to_datetime(
        date_end_1_year).timetuple().tm_yday

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
        df_values_aportacion_diario_1_year = df_values_aportacion_diario_all[
            df_values_aportacion_diario_all[ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA] >= date_init_today]
        df_values_aportacion_diario_1_year = df_values_aportacion_diario_1_year[
            df_values_aportacion_diario_1_year[ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA] <= date_end_1_year]

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
    df_datos_aportaciones_diario_1_year[CAMPO_FECHA_YYYY_MM] = pd.to_datetime(
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
        df_values_demanda_diario_1_year = pd.concat([df_values_demanda_diario_1_to_366.iloc[(date_init_today_day_of_year-1):N_DIAS_YEAR_ESTANDAR, :].copy(),
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
    df_datos_demandas_diario_1_year[CAMPO_FECHA_YYYY_MM] = df_datos_demandas_diario_1_year[CAMPO_FECHA].dt.strftime(
        '%Y-%m')

    # Reorder columns
    columnas = [CAMPO_FECHA, CAMPO_FECHA_YYYY_MM, CAMPO_VALOR,
                CFSDD_col_nombre, CFSDD_col_tipo_demanda_nombre]

    # Aplicar las columnas ordenadas
    df_datos_demandas_diario_1_year = df_datos_demandas_diario_1_year[columnas]
    df_datos_demandas_diario_1_year.reset_index(drop=True, inplace=True)

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
        df_demandas_a_considerar = df_pdf_demandas[(df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(1)] == n_retorno) |
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
            values_list_diario = list(map(add, values_list_diario, df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CFSDD_col_nombre] == demanda][CAMPO_VALOR].values *
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
    df_datos_retornos_diario_1_year[CAMPO_FECHA_YYYY_MM] = df_datos_retornos_diario_1_year[CAMPO_FECHA].dt.strftime(
        '%Y-%m')

    # Reorder columns
    columnas = [CAMPO_FECHA, CAMPO_FECHA_YYYY_MM,
                CAMPO_VALOR, CFSDR_col_nombre]

    # Aplicar las columnas ordenadas
    df_datos_retornos_diario_1_year = df_datos_retornos_diario_1_year[columnas]
    df_datos_retornos_diario_1_year.reset_index(drop=True, inplace=True)

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
        df_values_acuifero_diario_1_year = pd.concat([df_values_acuifero_diario_1_to_366.iloc[(date_init_today_day_of_year-1):N_DIAS_YEAR_ESTANDAR, :].copy(),
                                                      df_values_acuifero_diario_1_to_366.iloc[0:date_end_1_year_day_of_year-1, :].copy()], axis=0, ignore_index=True)

        # Tenemos el campo CAMPO_VALOR, añadimos otros campos de interés.
        # Para crear la fecha, convertimos el índice en un campo (que se llamará 'index')
        df_values_acuifero_diario_1_year.reset_index(inplace=True)

        # Ahora, creamos la fecha
        df_values_acuifero_diario_1_year[CAMPO_FECHA] = df_values_acuifero_diario_1_year['index'].apply(
            lambda x: pd.to_datetime((pd.to_datetime(date_init_today) + timedelta(days=x)).strftime('%Y-%m-%d')))

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
    df_datos_acuiferos_diario_1_year[CAMPO_FECHA_YYYY_MM] = df_datos_acuiferos_diario_1_year[CAMPO_FECHA].dt.strftime(
        '%Y-%m')

    # Reorder columns
    columnas = [CAMPO_FECHA, CAMPO_FECHA_YYYY_MM,
                CAMPO_VALOR, CFSDAC_col_nombre]

    # Aplicar las columnas ordenadas
    df_datos_acuiferos_diario_1_year = df_datos_acuiferos_diario_1_year[columnas]
    df_datos_acuiferos_diario_1_year.reset_index(drop=True, inplace=True)

    # 3. Calcular los datos de las aportaciones (aguas superficiales, del trasvase y desaladas), acuíferos (aguas subterráneas)
    # y retornos (aguas reutilizadas).

    # 3.1 Datos anuales.

    # 'superficial'
    g_cantidad_agua_superficial_1_year = \
        df_datos_aportaciones_diario_1_year[df_datos_aportaciones_diario_1_year[CFSDA_col_tipo_aportacion] == 'superficial'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'trasvase'
    g_cantidad_agua_trasvase_1_year = \
        df_datos_aportaciones_diario_1_year[df_datos_aportaciones_diario_1_year[CFSDA_col_tipo_aportacion] == 'trasvase'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'desalada'
    g_cantidad_agua_desalada_1_year = \
        df_datos_aportaciones_diario_1_year[df_datos_aportaciones_diario_1_year[CFSDA_col_tipo_aportacion] == 'desalada'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'subterranea'
    g_cantidad_agua_subterranea_1_year = df_datos_acuiferos_diario_1_year[CAMPO_VALOR].sum()

    # 'reutilizada'
    g_cantidad_agua_reutilizada_1_year = df_datos_retornos_diario_1_year[CAMPO_VALOR].sum()

    # TOTAL
    g_cantidad_agua_TOTAL_1_year = g_cantidad_agua_superficial_1_year + g_cantidad_agua_trasvase_1_year + \
        g_cantidad_agua_desalada_1_year + g_cantidad_agua_subterranea_1_year + g_cantidad_agua_reutilizada_1_year

    # Demandas 
    g_demandas_1_year = df_datos_demandas_diario_1_year[CAMPO_VALOR].sum()


    # 3.2  Datos de 15 días
    # Establecemos la fecha de aquí a 15 días
    date_end_15_days = (pd.to_datetime(date_init_today) +
                        timedelta(days=15)).strftime('%Y-%m-%d')

    # Filtramos los datos por fecha
    # APORTACIONES (superficial, trasvase, desalada)
    df_datos_aportaciones_diario_15_days = df_datos_aportaciones_diario_1_year[
        df_datos_aportaciones_diario_1_year[CAMPO_FECHA] <= date_end_15_days]

    # ACUIFEROS (subterráneas)
    df_datos_acuiferos_diario_15_days = df_datos_acuiferos_diario_1_year[
        df_datos_acuiferos_diario_1_year[CAMPO_FECHA] <= date_end_15_days]

    # RETORNOS (reutilizada)
    df_datos_retornos_diario_15_days = df_datos_retornos_diario_1_year[
        df_datos_retornos_diario_1_year[CAMPO_FECHA] <= date_end_15_days]

    # DEMANDAS
    df_datos_demandas_diario_15_days = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CAMPO_FECHA] <= date_end_15_days]

    # Desglosamos
    # 'superficial'
    g_cantidad_agua_superficial_15_days = df_datos_aportaciones_diario_15_days[df_datos_aportaciones_diario_15_days[
        CFSDA_col_tipo_aportacion] == 'superficial'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'trasvase'
    g_cantidad_agua_trasvase_15_days = df_datos_aportaciones_diario_15_days[df_datos_aportaciones_diario_15_days[
        CFSDA_col_tipo_aportacion] == 'trasvase'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'desalada'
    g_cantidad_agua_desalada_15_days = df_datos_aportaciones_diario_15_days[df_datos_aportaciones_diario_15_days[
        CFSDA_col_tipo_aportacion] == 'desalada'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'subterranea'
    g_cantidad_agua_subterranea_15_days = df_datos_acuiferos_diario_15_days[CAMPO_VALOR].sum(
    )

    # 'reutilizada'
    g_cantidad_agua_reutilizada_15_days = df_datos_retornos_diario_15_days[CAMPO_VALOR].sum(
    )

    # TOTAL
    g_cantidad_agua_TOTAL_15_days = g_cantidad_agua_superficial_15_days + g_cantidad_agua_trasvase_15_days + \
        g_cantidad_agua_desalada_15_days + g_cantidad_agua_subterranea_15_days + g_cantidad_agua_reutilizada_15_days

    # Demandas 
    g_demandas_15_days = df_datos_demandas_diario_15_days[CAMPO_VALOR].sum()

    # Ajustamos por si g_cantidad_agua_TOTAL_15_days y g_demandas_15_days no coinciden...
    g_cantidad_agua_superficial_15_days *= g_demandas_15_days/g_cantidad_agua_TOTAL_15_days
    g_cantidad_agua_trasvase_15_days *= g_demandas_15_days/g_cantidad_agua_TOTAL_15_days
    g_cantidad_agua_desalada_15_days *= g_demandas_15_days/g_cantidad_agua_TOTAL_15_days
    g_cantidad_agua_subterranea_15_days *= g_demandas_15_days/g_cantidad_agua_TOTAL_15_days
    g_cantidad_agua_reutilizada_15_days *= g_demandas_15_days/g_cantidad_agua_TOTAL_15_days    

    # 3.3 Datos de 7 meses
    # Establecemos la fecha de aquí a 7 meses
    date_end_7_months = (pd.to_datetime(
        date_init_today) + timedelta(days=(7*N_DIAS_MES_ESTANDAR))).strftime('%Y-%m-%d')

    # Filtramos los datos por fecha
    # APORTACIONES (superficial, trasvase, desalada)
    df_datos_aportaciones_diario_7_months = df_datos_aportaciones_diario_1_year[
        df_datos_aportaciones_diario_1_year[CAMPO_FECHA] <= date_end_7_months]

    # ACUIFEROS (subterráneas)
    df_datos_acuiferos_diario_7_months = df_datos_acuiferos_diario_1_year[
        df_datos_acuiferos_diario_1_year[CAMPO_FECHA] <= date_end_7_months]

    # RETORNOS (reutilizada)
    df_datos_retornos_diario_7_months = df_datos_retornos_diario_1_year[
        df_datos_retornos_diario_1_year[CAMPO_FECHA] <= date_end_7_months]

    # DEMANDAS
    df_datos_demandas_diario_7_months = \
        df_datos_demandas_diario_1_year[df_datos_demandas_diario_1_year[CAMPO_FECHA] <= date_end_7_months]

    # Desglosamos
    # 'superficial'
    g_cantidad_agua_superficial_7_months = df_datos_aportaciones_diario_7_months[df_datos_aportaciones_diario_7_months[
        CFSDA_col_tipo_aportacion] == 'superficial'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'trasvase'
    g_cantidad_agua_trasvase_7_months = df_datos_aportaciones_diario_7_months[df_datos_aportaciones_diario_7_months[
        CFSDA_col_tipo_aportacion] == 'trasvase'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'desalada'
    g_cantidad_agua_desalada_7_months = df_datos_aportaciones_diario_7_months[df_datos_aportaciones_diario_7_months[
        CFSDA_col_tipo_aportacion] == 'desalada'][ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].sum()

    # 'subterranea'
    g_cantidad_agua_subterranea_7_months = df_datos_acuiferos_diario_7_months[CAMPO_VALOR].sum(
    )

    # 'reutilizada'
    g_cantidad_agua_reutilizada_7_months = df_datos_retornos_diario_7_months[CAMPO_VALOR].sum(
    )

    # TOTAL
    g_cantidad_agua_TOTAL_7_months = g_cantidad_agua_superficial_7_months + g_cantidad_agua_trasvase_7_months + \
        g_cantidad_agua_desalada_7_months + g_cantidad_agua_subterranea_7_months + g_cantidad_agua_reutilizada_7_months

    # Demandas 
    g_demandas_7_months = df_datos_demandas_diario_7_months[CAMPO_VALOR].sum()

    # Ajustamos por si g_cantidad_agua_TOTAL_7_months y g_demandas_7_months no coinciden...
    g_cantidad_agua_superficial_7_months *= g_demandas_7_months/g_cantidad_agua_TOTAL_7_months
    g_cantidad_agua_trasvase_7_months *= g_demandas_7_months/g_cantidad_agua_TOTAL_7_months
    g_cantidad_agua_desalada_7_months *= g_demandas_7_months/g_cantidad_agua_TOTAL_7_months
    g_cantidad_agua_subterranea_7_months *= g_demandas_7_months/g_cantidad_agua_TOTAL_7_months
    g_cantidad_agua_reutilizada_7_months *= g_demandas_7_months/g_cantidad_agua_TOTAL_7_months

    # Return results

    # Resultados devueltos
    # 1. json con datos de 15 días
    # Primero, creamos un dataframe
    data_results_15_days = {'superficial': g_cantidad_agua_superficial_15_days,
                            'subterranea': g_cantidad_agua_subterranea_15_days,
                            'trasvase': g_cantidad_agua_trasvase_15_days,
                            'desalada': g_cantidad_agua_desalada_15_days,
                            'reutilizada': g_cantidad_agua_reutilizada_15_days}

    # 2. json con datos de 7 meses
    data_results_7_months = {'superficial': g_cantidad_agua_superficial_7_months,
                             'subterranea': g_cantidad_agua_subterranea_7_months,
                             'trasvase': g_cantidad_agua_trasvase_7_months,
                             'desalada': g_cantidad_agua_desalada_7_months,
                             'reutilizada': g_cantidad_agua_reutilizada_7_months}

    # Devolvemos
    return data_results_15_days, data_results_7_months
