#!/usr/bin/env python
# coding: utf-8

#########################################################################################################
#                                                                                                       #
# CHS's Hydrological model                                                                              #
# COMMENTS for v9.1			                                                                            #
#                                                                                                       #
#########################################################################################################


#####################
# LIBRARIES			#
#####################

# General
import sys
import getopt  # Library used for Command-Line Arguments management
import os.path  # Library used for file existance checking management
import logging
from flask import current_app

# Maths operations
import random
from operator import add

# Time management
from datetime import datetime, timedelta
import time

# Data Science
import pandas as pd
import numpy as np

# pywr
from pywr.core import Timestepper, Model, Link, Storage, Input, Output, MultiSplitLink, LossLink
from pywr.recorders import NumpyArrayNodeRecorder, NumpyArrayStorageRecorder, MinimumVolumeStorageRecorder, \
    DeficitFrequencyNodeRecorder
from pywr.dataframe_tools import load_dataframe
from pywr.parameters import load_parameter, MonthlyProfileParameter, DailyProfileParameter

DATA_FOLDER = current_app.config['DATA_FOLDER']

#####################################
# Exit code error constants			#
#####################################

# Exit code error constant
EXIT_CODE_SCRIPT_CALL_OPTIONS_ERROR = -1
EXIT_CODE_FILE_MISSING_AS_ARGUMENT = -2
EXIT_CODE_FILE_DOES_NOT_EXIST = -3
EXIT_CODE_FILE_EQUAL_FILE_NAMES = -4
EXIT_CODE_FILE_CANNOT_BE_OPENED = -5
EXIT_CODE_EXCEL_SHEET_CANNOT_BE_OPENED = -6
EXIT_CODE_CELL_VALUE_DOES_NOT_EXIST = -7
EXIT_CODE_INCORRECT_CONFIG_PARAMETER = -8
EXIT_CODE_MAPPING_TAG_NOT_FOUND = -9
EXIT_CODE_FILE_HAS_NAN_VALUES = -10
EXIT_CODE_FILE_HAS_NON_NUMERIC_VALUES = -11
EXIT_CODE_OUT_FILE_INCONSISTENCY = -12
EXIT_CODE_FILE_CANNOT_BE_SAVED = -13
EXIT_CODE_GENERIC_ERROR = -99


#####################################
# Application constants			    #
#####################################

# CONFIG FILES AND THEIR SHEETS AND COLUMNS

# GENERIC CONFIG FILE
CONFIG_FILE = DATA_FOLDER + '/L4/Model/CONFIG/CONFIG_FILE_tpl.tpa_dataframe_to_pywr.xlsx'

# SHEET and COLUMNS FOR tpa_to_dataframe_file, physical_data_file, exceptions_file and out_file
# IN FILE
CF_SHEET_IN_FILE_tpa_dataframe_file = 'IN_tpa_to_dataframe_file'
CFSIFtdf_HEADER = 0
CFSIFtdf_input_file_path = 'IN_tpa_to_dataframe_file_path'
CFSIFtdf_sheet = 'sheet'
CFSIFtdf_header = 'header'
CFSIFtdf_col_tipo_elemento_nombre = 'col_tipo_elemento_nombre'
CFSIFtdf_col_elemento_id = 'col_elemento_id'
CFSIFtdf_col_elemento_num_user = 'col_elemento_num_user'
CFSIFtdf_col_elemento_nombre = 'col_elemento_nombre'
CFSIFtdf_col_elemento_nodo_origen = 'col_elemento_nodo_origen'
CFSIFtdf_col_elemento_nodo_destino_demanda = 'col_elemento_nodo_destino_demanda'
CFSIFtdf_col_elemento_nodo_destino_retorno = 'col_elemento_nodo_destino_retorno'
CFSIFtdf_col_nombre_nodo_final = 'nombre_nodo_final'
CFSIFtdf_col_tipo_demanda = 'col_tipo_demanda'
CFSIFtdf_col_tipo_demanda_nombre = 'col_tipo_demanda_nombre'
CFSIFtdf_col_demanda_mi_id = 'col_demanda_mi_id'

# PHYSICAL DATA FILE
CF_SHEET_IN_FILE_physical_data_file = 'IN_physical_data_file'
CFSIFpdf_HEADER = 0
CFSIFpdf_physical_data_file_path = 'IN_physical_data_file_path'
CFSIFpdf_sheet_datos_generales = 'sheet_datos_generales'
CFSIFpdf_header_general = 'header_general'

#####---------------------------------------#####
##### Sheets especiales y sus constantes    #####
#####---------------------------------------#####

CFSIFpdf_sheet_embalses = 'sheet_embalses'
CFSIFpdf_sheet_aportaciones = 'sheet_aportaciones'
CFSIFpdf_sheet_demandas = 'sheet_demandas'
CFSIFpdf_sheet_conducciones1 = 'sheet_conducciones1'
CFSIFpdf_sheet_conducciones3 = 'sheet_conducciones3'
CFSIFpdf_sheet_bombeos = 'sheet_bombeos'
CFSIFpdf_sheet_acuiferos = 'sheet_acuiferos'
CFSIFpdf_sheet_retornos = 'sheet_retornos'

#####---------------------------------------#####
##### Constantes para los sheets especiales #####
#####---------------------------------------#####

# ---EMBALSES
CFSDE_col_nombre = 'nombre'
CFSDE_col_columna_aportaciones = 'columna_aportaciones'
CFSDE_col_columna_evaporaciones = 'columna_evaporaciones'
CFSDE_col_n_prioridad = 'n_prioridad'
CFSDE_col_n_acuif_al_que_infiltra = 'n_acuif_al_que_infiltra'
CFSDE_col_n_accion_infiltra = 'n_accion_infiltra'
CFSDE_col_vol_inicial = 'vol_inicial_Hm3'
CFSDE_col_q_max_sueltas = 'q_max_sueltas_Hm3_mes'
CFSDE_col_v_max_mensual_12_vals = 'v_max_mensual_12_vals_Hm3'
CFSDE_col_v_obj_mensual_12_vals = 'v_obj_mensual_12_vals_Hm3'
CFSDE_col_v_min_mensual_12_vals = 'v_min_mensual_12_vals_Hm3'
CFSDE_col_cota_10_vals = 'cota_10_vals_m'
CFSDE_col_superf_10_vals = 'superf_10_vals_Ha'
CFSDE_col_vol_10_vals = 'vol_10_vals_Hm3'
CFSDE_col_evapo_mensual_12_vals = 'evapo_mensual_12_vals_mm'

# ---APORTACIONES
CFSDA_col_nombre = 'nombre'
CFSDA_col_nudo_destino = 'nudo_destino'
CFSDA_col_columna_en_archivo_aportaciones = 'columna_en_archivo_aportaciones'

# ---DEMANDAS
CFSDD_max_n_tomas = 5
CFSDD_col_nombre = 'nombre'
CFSDD_col_demanda_mensual_12_vals = 'demanda_mensual_12_vals_Hm3'
CFSDD_col_n_acuif_al_que_recarga = 'n_acuif_al_que_recarga'
CFSDD_col_n_accion_recarga = 'n_accion_recarga'
CFSDD_col_n_acuif_del_que_bombea = 'n_acuif_del_que_bombea'
CFSDD_col_n_accion_bombeo = 'n_accion_bombeo'
CFSDD_col_q_max_mensual_bombeo = 'q_max_mensual_bombeo_Hm3'
CFSDD_col_coef_garantia_mensual_A = 'coef_garantia_mensual_A'
CFSDD_col_coef_garantia_B = 'coef_garantia_B'
CFSDD_col_coef_garantia_C = 'coef_garantia_C'
CFSDD_col_coef_garantia_D = 'coef_garantia_D'
CFSDD_col_coef_garantia_E = 'coef_garantia_E'
CFSDD_col_coef_garantia_F = 'coef_garantia_F'
CFSDD_col_coef_garantia_G = 'coef_garantia_G'
CFSDD_col_coef_garantia_H = 'coef_garantia_H'
CFSDD_col_n_tomas = 'n_tomas'
CFSDD_col_nombre_toma = 'nombre_toma'
CFSDD_col_nudo_toma = 'nudo_toma'
CFSDD_col_cota_toma = 'cota_toma'
CFSDD_col_dotacion_anual = 'dotacion_anual_Hm3'
CFSDD_col_coef_retorno = 'coef_retorno'
CFSDD_col_coef_consumo = 'coef_consumo'
CFSDD_col_n_prioridad = 'n_prioridad'
CFSDD_col_n_elemento_retorno = 'n_elemento_retorno'
CFSDD_col_valor_punta_mensual_12_vals = 'valor_punta_mensual_12_vals_Hm3'

# ---CONDUCCIONES1
CFSDC1_col_nombre = 'nombre'
CFSDC1_col_vol_max_anual = 'vol_max_anual_Hm3'
CFSDC1_col_n_prioridad_qmin = 'n_prioridad_qmin'
CFSDC1_col_coste_tipo = 'coste_tipo'
CFSDC1_col_coste_flujo = 'coste_flujo'
CFSDC1_col_nivel_fallo_qmin_admisible = 'nivel_fallo_qmin_admisible'
CFSDC1_col_qmin_mensual_12_vals = 'qmin_mensual_12_vals_Hm3'
CFSDC1_col_qmax_mensual_12_vals = 'qmax_mensual_12_vals_Hm3'

# ---CONDUCCIONES3
CFSDC3_col_nombre = 'nombre'
CFSDC3_col_n_prioridad_qmin = 'n_prioridad_qmin'
CFSDC3_col_nivel_fallo_qmin_admisible = 'nivel_fallo_qmin_admisible'
CFSDC3_col_qmin_mensual_12_vals = 'qmin_mensual_12_vals_Hm3'
CFSDC3_col_qmax_mensual_12_vals = 'qmax_mensual_12_vals_Hm3'
CFSDC3_col_n_acuif_conectado = 'n_acuif_conectado'

# ---BOMBEOS
CFSDB_col_nombre = 'nombre'
CFSDB_col_n_acuif_del_que_bombea = 'n_acuif_del_que_bombea'
CFSDB_col_q_maximo_mensual_a_bombear = 'q_maximo_mensual_a_bombear_Hm3'
CFSDB_col_nudo_destino = 'nudo_destino'
CFSDB_col_nivel_suministro_maximo = 'nivel_suministro_maximo'

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

# EXCEPTIONS FILE
CF_SHEET_EXCEPTIONS_FILE = 'OUT_exceptions_file'
CFSEF_HEADER = 0
CFSEF_exceptions_file_path = 'OUT_exceptions_file_path'
CFSEF_col_sheet_exceptions = 'sheet_exceptions'
CFSEF_col_id = 'col_id'
CFSEF_col_name = 'col_name'
CFSEF_col_type = 'col_type'

# OUT FILE
CF_SHEET_OUT_FILE = 'OUT_results_file'
CFSOF_HEADER = 0
CFSOF_output_file_path = 'OUT_results_file_path'
CFSOF_col_sheet_nudo_final = 'sheet_nudo_final'
CFSOF_col_sheet_embalses = 'sheet_embalses'
CFSOF_col_sheet_aportaciones = 'sheet_aportaciones'
CFSOF_col_sheet_demandas = 'sheet_demandas'
CFSOF_col_sheet_tomas = 'sheet_tomas'
CFSOF_col_sheet_conducciones1 = 'sheet_conducciones1'
CFSOF_col_sheet_conducciones3 = 'sheet_conducciones3'
CFSOF_col_sheet_bombeos = 'sheet_bombeos'
CFSOF_col_sheet_retornos_input = 'sheet_retornos_input'
CFSOF_col_sheet_retornos_output = 'sheet_retornos_output'
CFSOF_col_sheet_acuiferos = 'sheet_acuiferos'
CFSOF_col_sheet_retorno_global = 'sheet_retorno_global'
CFSOF_col_sheet_totales = 'sheet_totales'

# Node and time identification columns
CFSOF_col_id = 'col_id'
CFSOF_col_name = 'col_name'
CFSOF_col_timestamp = 'col_timestamp'

# Flow data
CFSOF_col_flow = 'col_flow'
CFSOF_col_mean_flow = 'col_mean_flow'
CFSOF_col_init_min_flow = 'col_init_min_flow'
CFSOF_col_init_max_flow = 'col_init_max_flow'
CFSOF_col_flow_supplied_rate = 'col_flow_supplied_rate'
CFSOF_col_flow_deficit = 'col_flow_deficit'
CFSOF_col_flow_deficit_percent = 'col_flow_deficit_percent'
CFSOF_col_flow_deficit_frequency = 'col_flow_deficit_frequency'

CFSOF_col_total_flow = 'col_total_flow'
CFSOF_col_total_init_max_flow = 'col_total_init_max_flow'
CFSOF_col_total_flow_supplied_rate = 'col_total_flow_supplied_rate'
CFSOF_col_total_flow_deficit = 'col_total_flow_deficit'
CFSOF_col_total_flow_deficit_percent = 'col_total_flow_deficit_percent'

# Volume data

CFSOF_col_volume = 'col_volume'
CFSOF_col_min_volume = 'col_min_volume'
CFSOF_col_init_vol = 'col_init_vol'
CFSOF_col_init_min_vol = 'col_init_min_vol'
CFSOF_col_init_max_vol = 'col_init_max_vol'
CFSOF_col_cost = 'col_cost'
CFSOF_col_split_factor_demanda = 'col_split_factor_demanda'
CFSOF_col_split_factor_retorno = 'col_split_factor_retorno'
CFSOF_col_conduccion_factor_perdida = 'col_conduccion_factor_perdida'

# Other values: total aggregation values for elements
# Previsto
CFSOF_col_total_flow_aportaciones_all_prev = 'col_total_flow_aportaciones_all_prev'
CFSOF_col_total_flow_retornos_input_all_prev = 'col_total_flow_retornos_input_all_prev'
CFSOF_col_total_flow_acuiferos_all_prev = 'col_total_flow_acuiferos_all_prev'
CFSOF_col_total_flow_retornos_output_all_prev = 'col_total_flow_retornos_output_all_prev'
CFSOF_col_total_flow_demandas_all_prev = 'col_total_flow_demandas_all_prev'
# suma de todas las entradas (aportaciones, retornos-input, acuiferos).
CFSOF_col_total_flow_INPUT_all_prev = 'col_total_flow_INPUT_all_prev'
# suma de todas las salidas (retornos-output, demandas).
CFSOF_col_total_flow_OUTPUT_all_prev = 'col_total_flow_OUTPUT_all_prev'

# Real
CFSOF_col_total_flow_aportaciones_all_real = 'col_total_flow_aportaciones_all_real'
CFSOF_col_total_flow_tomas_all_real = 'col_total_flow_tomas_all_real'
CFSOF_col_total_flow_retornos_input_all_real = 'col_total_flow_retornos_input_all_real'
CFSOF_col_total_flow_acuiferos_all_real = 'col_total_flow_acuiferos_all_real'
CFSOF_col_total_flow_retornos_output_all_real = 'col_total_flow_retornos_output_all_real'
CFSOF_col_total_flow_demandas_all_real = 'col_total_flow_demandas_all_real'
CFSOF_col_total_flow_bombeos_all_real = 'col_total_flow_bombeos_all_real'
# suma de todas las entradas (aportaciones, retornos-input, acuiferos).
CFSOF_col_total_flow_INPUT_all_real = 'col_total_flow_INPUT_all_real'
# suma de todas las salidas (retornos-output, demandas).
CFSOF_col_total_flow_OUTPUT_all_real = 'col_total_flow_OUTPUT_all_real'

# Deficit (%)
CFSOF_col_total_flow_aportaciones_all_supplied_rate = 'col_total_flow_aportaciones_all_supplied_rate'
CFSOF_col_total_flow_retornos_input_all_supplied_rate = 'col_total_flow_retornos_input_all_supplied_rate'
CFSOF_col_total_flow_acuiferos_all_supplied_rate = 'col_total_flow_acuiferos_all_supplied_rate'
CFSOF_col_total_flow_retornos_output_all_deficit_percent = 'col_total_flow_retornos_output_all_deficit_percent'
CFSOF_col_total_flow_demandas_all_deficit_percent = 'col_total_flow_demandas_all_deficit_percent'
# suma de todas las entradas (aportaciones, retornos-input, acuiferos).
CFSOF_col_total_flow_INPUT_all_supplied_rate = 'col_total_flow_INPUT_all_supplied_rate'
# suma de todas las salidas (retornos-output, demandas).
CFSOF_col_total_flow_OUTPUT_all_deficit_percent = 'col_total_flow_OUTPUT_all_deficit_percent'

# ------------------------- #

# Constantes generales
NODE_TYPE_NAME_PREFIX = "<class 'pywr.nodes."
NODE_TYPE_NAME_SUFFIX = "'>"

# ------------------------- #

# Constantes de inicialización (ARTIFICIAL) de elementos
# NOTA: por el momento, definimos listas de valores, para que de forma ARTIFICIAL y aleatoria, se pueda utilizar alguno de
# dichos valores en la inicialización.

# (0) Nudo <---> Link

# Por el momento, a los nodos no se les define ningún parámetro

# (1) Embalse <---> Storage

lstC_ARTIFICIAL_embalse_init_vol = [5, 15, 25]
lstC_ARTIFICIAL_embalse_min_vol = [5, 15, 25]
lstC_ARTIFICIAL_embalse_max_vol = [50, 150, 250]
lstC_ARTIFICIAL_embalse_max_flow = [10, 20, 30]
lstC_ARTIFICIAL_embalse_cost = [0, 1, 2, 3]

# (2) Aportacion <---> Input
lstC_ARTIFICIAL_aportacion_max_flow = [10, 20, 30]

# (3) Demanda <---> Output
lstC_ARTIFICIAL_demanda_max_flow = [100, 200, 300]
lstC_ARTIFICIAL_demanda_cost = [-10, -20, -30, -40, -50]

# (4) Toma <---> MultiSplitLink
lstC_ARTIFICIAL_toma_split_retorno = [0.1, 0.2, 0.3]

# (5) Conduccion1 <---> LossLink
lstC_ARTIFICIAL_conduccion1_loss_factor = [0.1, 0.2, 0.3]

# (6) Conduccion3 <---> LossLink
lstC_ARTIFICIAL_conduccion3_loss_factor = [0.05, 0.1, 0.15]

# (7) Bombeo <---> Link
lstC_ARTIFICIAL_bombeo_cost = [1, 2, 3]

# (8) Retorno <---> Input + Output
# Parte Input
# NOTA: por el momento, como los retornos no están conectados, asumimos que tienen un valor de max_flow.
#       como los retornos son de todo tipo, se definen diversos costes para esos tipos.
lstC_ARTIFICIAL_retorno_input_max_flow = [0, 1, 2, 4]
lstC_ARTIFICIAL_retorno_input_cost = [2, 4, 6, 8, 10, 12]

# (9) Acuifero <---> Input [+ Storage]
lstC_ARTIFICIAL_acuifero_init_vol = [2, 6, 10]
lstC_ARTIFICIAL_acuifero_min_vol = [2, 6, 10]
lstC_ARTIFICIAL_acuifero_max_vol = [20, 60, 100]
lstC_ARTIFICIAL_acuifero_max_flow = [4, 8, 12]
lstC_ARTIFICIAL_acuifero_cost = [2, 8]

# NOTA: los valores de los beneficios de las demandas se determinarán de la siguiente manera:
# (a) Se analizarán todas las rutas de las demandas hacia atrás, con el fin de determinar
# el balance del coste de cada ruta.
# (b) De todos ellos, se determinará el valor de balance de coste más grande (max_coste).
# (c) Una vez de haver determinado dicho valor, se establecerá un valor de beneficio mediante la siguiente fórmula:
#####                               beneficio_demanda = (-max_coste-1)+(lstC_ARTIFICIAL_demanda_cost[i])
# donde i será un valor aleatorio entre 0 y len(lstC_ARTIFICIAL_demanda_cost)-1.

# ------------------------- #

# Constantes de inicialización (REAL, valores SIMGES) de elementos

# Constantes para definición de parámetros
PARAM_NOMBRE_vol_min_values_MENSUAL = 'PARAM_vol_min_values_MENSUAL_'
PARAM_NOMBRE_vol_max_values_MENSUAL = 'PARAM_vol_max_values_MENSUAL_'
PARAM_NOMBRE_vol_min_values_DIARIO = 'PARAM_vol_min_values_DIARIO_'
PARAM_NOMBRE_vol_max_values_DIARIO = 'PARAM_vol_max_values_DIARIO_'
PARAM_NOMBRE_q_min_values_MENSUAL = 'PARAM_q_min_values_MENSUAL_'
PARAM_NOMBRE_q_max_values_MENSUAL = 'PARAM_q_max_values_MENSUAL_'
PARAM_NOMBRE_q_min_values_DIARIO = 'PARAM_q_min_values_DIARIO_'
PARAM_NOMBRE_q_max_values_DIARIO = 'PARAM_q_max_values_DIARIO_'

N_MESES_YEAR_ESTANDAR = 12  # Generic constant
N_DIAS_MES_ESTANDAR = 30  # Generic constant
N_DIAS_YEAR_ESTANDAR = 366  # Generic constant

# DIRECTORIO DE SALIDA DE ARCHIVOS .csv DE APORTACIONES
PARAMETROS_APORTACIONES_DIRECTORIO_MENSUAL = DATA_FOLDER + '/L4/Model/PARAMETROS/APORTACIONES/MENSUAL/'
PARAMETROS_APORTACIONES_DIRECTORIO_DIARIO = DATA_FOLDER + '/L4/Model/PARAMETROS/APORTACIONES/DIARIO/'
PREFIJO_ARCHIVO_CSV_APORTACIONES_MENSUAL = 'APORTACION_M_'
PREFIJO_ARCHIVO_CSV_APORTACIONES_DIARIO = 'APORTACION_D_'
ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA = 'fecha'
ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR = 'valor'

# Constantes para definición de tablas (para parámetros) y parámetros para APORTACIONES
TABLA_NOMBRE_aportaciones_MENSUAL = 'TABLA_aportaciones_MENSUAL_'
TABLA_NOMBRE_aportaciones_DIARIO = 'TABLA_aportaciones_DIARIO_'
PARAM_NOMBRE_aportaciones_MENSUAL = 'PARAM_aportaciones_MENSUAL_'
PARAM_NOMBRE_aportaciones_DIARIO = 'PARAM_aportaciones_DIARIO_'

# Constantes para definición de parámetros para DEMANDAS
PARAM_NOMBRE_demanda_values_MENSUAL = 'PARAM_demanda_values_MENSUAL_'
PARAM_NOMBRE_demanda_values_DIARIO = 'PARAM_demanda_values_DIARIO_'

# Constantes para definición de parámetros para RETORNOS
PARAM_NOMBRE_demanda_retorno_values_MENSUAL = 'PARAM_demanda_retorno_values_MENSUAL_'
PARAM_NOMBRE_demanda_retorno_values_DIARIO = 'PARAM_demanda_retorno_values_DIARIO_'

# Constantes para definición de parámetros para ACUIFEROS
PARAM_NOMBRE_recarga_acuifero_values_MENSUAL = 'PARAM_recarga_acuifero_values_MENSUAL_'
PARAM_NOMBRE_recarga_acuifero_values_DIARIO = 'PARAM_recarga_acuifero_values_DIARIO_'

# ------------------------- #

# Constantes de pasos de simulación
SIMULATION_STEP_PASO_DIARIO = 1
SIMULATION_STEP_PASO_MENSUAL = 2

# Constantes de tipos simulación
SIMULATION_TYPE_PLANNING = 1
SIMULATION_TYPE_OPTIMISATION = 2

# DEFINIMOS ESTA CONSTANTE PORQU POR EL MOMENTO NO CONSEGUIMOS SIMULAR MÁS DE 9 MESES
MAX_N_MESES_SIMUL = 9

# ------------------------- #


# Auxiliary variables
blnInicializar_con_valores_artificiales_y_n = False
blnEliminar_nodos_aislados_y_n = True


################################
# GENERAL AUXILIARY FUNCTIONS  #
################################

# ******************************************************************************************************
# FUNCTION: MyErrorHandling(p_error_messages, p_error_code, p_terminate_y_n=True)
#
# DESCRIPTION: Print an error message and terminate the execution of the program, if requested.
#
# ARGUMENTS:
# 	p_error_messages: list of strings making up the error message.
#	p_error_code: program error code.
#   p_terminate_y_n: whether or not program must be terminated (True/False).
# ******************************************************************************************************
def MyErrorHandling(p_error_messages, p_error_code, p_terminate_y_n=True):
    print('\nWARNING!!!')
    for i in range(len(p_error_messages)):
        print(p_error_messages[i])
    logging.error(f'Exit code {-1*p_error_code}: {p_error_messages}')
    if (p_terminate_y_n):
        sys.exit(p_error_code)


# ******************************************************************************************************
# FUNCTION: ValidateDateInput(p_date_text)
#
# DESCRIPTION: Return True if p_date_text has format '%Y-%m-%d'; otherwise, return False.
#
# ARGUMENTS:
# 	p_date_text: input string / text, supposed to be a date.
# ******************************************************************************************************
def ValidateDateInput(p_date_text):
    try:
        datetime.strptime(p_date_text, '%Y-%m-%d')
        return(True)
    except ValueError:
        return(False)


################################
# SPECIFIC AUXILIARY FUNCTIONS #
################################

# Auxiliary function to get Node type name
def GetNodeTypeName(p_node):
    strNode_name = str(p_node.__class__)
    strNode_name = strNode_name.split("<class 'pywr.nodes.")[1].split("'>")[0]
    return strNode_name


# Auxiliary function to get node's predecessor list
#       (1) nodos de tipo Storage:
#           + La lista de nodos predecesores se encuentra en su propiedad .outputs[0]. Ejemplo:
#
#             storage_predecessors = list(storage.outputs[0].model.graph.predecessors(storage.outputs[0]))
#
#       (2) nodos de tipo MultiSplitLink:
#           + La lista de nodos predecesores se encuentra en su propiedad .output. Ejemplo:
#
#             multi_split_link_predecessors = list(multi_split_link.output.model.graph.predecessors(multi_split_link.output))
#
#       (3) nodos de tipo LossLink:
#           + La lista de nodos predecesores se encuentra en su propiedad .gross. Ejemplo:
#
#             loss_link_predecessors = list(loss_link.gross.model.graph.predecessors(loss_link.gross))
#
#       (4) resto de tipo de nodos aquí utilizados (Node, Input, Output, Link) :
#           + La lista de nodos predecesores se encuentra desde el propio nodo. Ejemplo:
#
#             predecessors_nodo = list(nodo.gross.model.graph.predecessors(nodo))
#
def GetPredecessorList(p_nodo):
    strTipo_nodo = GetNodeTypeName(p_nodo)
    if (strTipo_nodo == 'Storage'):
        return list(p_nodo.outputs[0].model.graph.predecessors(p_nodo.outputs[0]))
    elif (strTipo_nodo == 'MultiSplitLink'):
        return list(p_nodo.output.model.graph.predecessors(p_nodo.output))
    elif (strTipo_nodo == 'LossLink'):
        return list(p_nodo.gross.model.graph.predecessors(p_nodo.gross))
    else:
        return list(p_nodo.model.graph.predecessors(p_nodo))


# Auxiliary function to get node's sucessor list
#       (1) nodos de tipo Storage:
#           + La lista de nodos sucesores se encuentra en su propiedad .inputs[0]. Ejemplo:
#
#             storage_successors = list(storage.inputs[0].model.graph.successors(storage.inputs[0]))
#
#       (2) nodos de tipo MultiSplitLink:
#           + La lista de nodos sucesores se encuentra en sus propiedades .inputs y ._extra_inputs[n],
#             donde n toma valores entra 0 y n_extra_slots - 1. Como el nuestro siempre caso n_extra_slots = 1, podemos decir
#             que La lista de nodos sucesores se encuentra en sus propiedades .inputs y ._extra_inputs[0]. Ejemplo:
#
#             multi_split_link_successors_1 = list(multi_split_link.input.model.graph.successors(multi_split_link.input))
#             multi_split_link_successors_2 = list(multi_split_link._extra_inputs[0].model.graph.successors(multi_split_link._extra_inputs[0]))
#
#       (3) nodos de tipo LossLink:
#           + La lista de nodos sucesores se encuentra en su propiedad .net. Ejemplo:
#
#             loss_link_successors = list(loss_link.net.model.graph.successors(loss_link.net))
#
#       (4) resto de tipo de nodos aquí utilizados (Node, Input, Output, Link) :
#           + La lista de nodos sucesores se encuentra desde el propio nodo. Ejemplo:
#
#             successors_nodo = list(nodo.gross.model.graph.successors(nodo))
#
def GetSuccessorList(p_nodo):
    strTipo_nodo = GetNodeTypeName(p_nodo)
    if (strTipo_nodo == 'Storage'):
        return list(p_nodo.inputs[0].model.graph.successors(p_nodo.inputs[0]))
    elif (strTipo_nodo == 'MultiSplitLink'):
        list_1 = list(p_nodo.input.model.graph.successors(p_nodo.input))
        list_2 = list(p_nodo._extra_inputs[0].model.graph.successors(
            p_nodo._extra_inputs[0]))
        return (list_1+list_2)
    elif (strTipo_nodo == 'LossLink'):
        return list(p_nodo.net.model.graph.successors(p_nodo.net))
    else:
        return list(p_nodo.model.graph.successors(p_nodo))


# Auxiliary function to get mode's largest cost. The cost paths is calculated and largest resturned.
def CalculateModelLargestCost(p_nodo, p_coste_ruta, p_max_coste_ruta):

    # Add current node's cost
    try:
        p_coste_ruta += p_nodo.cost

    except Exception as error_msg:
        #    print(error_msg)
        # Do nothing
        mi_mensaje = error_msg

    # Get current's node's predecesor list and iterate it.
    lstPredecesores = GetPredecessorList(p_nodo)
    for i in range(len(lstPredecesores)):
        nodo = lstPredecesores[i].parent
        if (nodo == None):
            nodo = lstPredecesores[i]
        p_coste_ruta, p_max_coste_ruta = CalculateModelLargestCost(
            nodo, p_coste_ruta, p_max_coste_ruta)
    if (p_coste_ruta > p_max_coste_ruta):
        p_max_coste_ruta = p_coste_ruta  # Upgrade p_max_coste_ruta.

    try:
        # Once node's predecesors list has been iterated, subtract current node's cost
        p_coste_ruta -= p_nodo.cost

    except Exception as error_msg:
        #    print(error_msg)
        # Do nothing
        mi_mensaje = error_msg

    # Return
    return(p_coste_ruta, p_max_coste_ruta)


# Función auxiliar para verificar si un elemento / nodo de retorno se encuentra entre los destinos de algún elemento / nodo
# de demanda del archivo de datos físicos.
def VerificarSiNodoEsRetornoDeNodoDeDemandaEnArchivoDatosFisicos(p_retorno_nombre, p_df_pdf_retornos, p_df_pdf_demandas):

    # Primero, comprobar si el retorno se encuentra entre los retornos del fichero de datos físicos.
    # NOTA: recordar que en el archivo de datos físicos, los nombres de los nodos /elementos tienen " al principio y al final.
    df_retorno = p_df_pdf_retornos[p_df_pdf_retornos[CFSDR_col_nombre]
                                   == '"' + p_retorno_nombre + '"']
    if (df_retorno.shape[0] > 0):
        # A continuación, comprobar si es un destino de alguna toma de demanda
        for i in range(CFSDD_max_n_tomas):
            df_toma = p_df_pdf_demandas[p_df_pdf_demandas[CFSDD_col_n_elemento_retorno + '_' + str(
                i+1)] == df_retorno[CFSDR_col_n_retorno].values[0]]
            if (df_toma.shape[0] > 0):  # Se ha encontrado la toma
                return(True)
    else:
        print("WARNING: Función 'VerificarSiNodoEsRetornoDeNodoDeDemandaEnArchivoDatosFisicos'; no se ha encontrado el RETORNO.")

    # Si llegamos hasta aquí, es que el retorno no es destino de ninguna demanda.
    return(False)


###############################################################################
# Funciones auxiliares de inicialización de datos de manera ARTIFICIAL
###############################################################################

# Función auxiliar para inicializar los embalses
# (1) Embalse <---> Storage
def InicializarEmbalse_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.initial_volume = lstC_ARTIFICIAL_embalse_init_vol[random.randint(
            0, len(lstC_ARTIFICIAL_embalse_init_vol)-1)]
        p_nodo.min_volume = lstC_ARTIFICIAL_embalse_min_vol[random.randint(
            0, len(lstC_ARTIFICIAL_embalse_min_vol)-1)]
        p_nodo.max_volume = lstC_ARTIFICIAL_embalse_max_vol[random.randint(
            0, len(lstC_ARTIFICIAL_embalse_max_vol)-1)]
        p_nodo.max_flow = lstC_ARTIFICIAL_embalse_max_flow[random.randint(
            0, len(lstC_ARTIFICIAL_embalse_max_flow)-1)]
        p_nodo.cost = lstC_ARTIFICIAL_embalse_cost[random.randint(
            0, len(lstC_ARTIFICIAL_embalse_cost)-1)]
    return (p_nodo)

# Función auxiliar para inicializar las aportaciones
# (2) Aportacion <---> Input


def InicializarAportacion_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.max_flow = lstC_ARTIFICIAL_aportacion_max_flow[random.randint(
            0, len(lstC_ARTIFICIAL_aportacion_max_flow)-1)]
    return (p_nodo)

# Función auxiliar para inicializar las demandas
# (3) Demanda <---> Output


def InicializarDemanda_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.max_flow = lstC_ARTIFICIAL_demanda_max_flow[random.randint(
            0, len(lstC_ARTIFICIAL_demanda_max_flow)-1)]
        p_nodo.cost = lstC_ARTIFICIAL_demanda_cost[random.randint(
            0, len(lstC_ARTIFICIAL_demanda_cost)-1)]
    return (p_nodo)

# Función auxiliar para inicializar las tomas
# (4) Toma <---> MultiSplitLink


def InicializarToma_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        factor_retorno = lstC_ARTIFICIAL_toma_split_retorno[random.randint(
            0, len(lstC_ARTIFICIAL_toma_split_retorno)-1)]
        factor_demanda = 1.0 - factor_retorno
        p_nodo.factors = [factor_demanda, factor_retorno]
    return (p_nodo)

# Función auxiliar para inicializar las conducciones1
# (5) Conduccion1 <---> LossLink


def InicializarConduccion1_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.loss_factor = lstC_ARTIFICIAL_conduccion1_loss_factor[random.randint(
            0, len(lstC_ARTIFICIAL_conduccion1_loss_factor)-1)]
    return (p_nodo)

# Función auxiliar para inicializar las conducciones3
# (6) Conduccion3 <---> LossLink


def InicializarConduccion3_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.loss_factor = lstC_ARTIFICIAL_conduccion3_loss_factor[random.randint(
            0, len(lstC_ARTIFICIAL_conduccion3_loss_factor)-1)]
    return (p_nodo)

# Función auxiliar para inicializar los bombeos
# (7) Bombeo <---> Link


def InicializarBombeo_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.cost = lstC_ARTIFICIAL_bombeo_cost[random.randint(
            0, len(lstC_ARTIFICIAL_bombeo_cost)-1)]
    return (p_nodo)

# Función auxiliar para inicializar los retornos
# (8) Retorno <---> Input + Output
# Parte Input
# NOTA: por el momento, como los retornos no están conectados, asumimos que tienen un valor de max_flow.
# Como los retornos son de todo tipo, los costes los estableceremos de diferentes tipos.


def InicializarRetorno_Input_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        p_nodo.max_flow = lstC_ARTIFICIAL_retorno_input_max_flow[random.randint(
            0, len(lstC_ARTIFICIAL_retorno_input_max_flow)-1)]
        p_nodo.cost = lstC_ARTIFICIAL_retorno_input_cost[random.randint(
            0, len(lstC_ARTIFICIAL_retorno_input_cost)-1)]
    return (p_nodo)

# Función que iguala los valores de inicialización de retorno_output con respecto a retorno_input


def IgualarValoresInicializacionRetornos_ARTIFICIAL(p_nodo_retorno_output, p_dic_retornos_input):

    # IMPORTANTE: recordar que el ID del retorno en dic_retornos_input tiene el sufijo '_input' y en dic_retornos_output
    #             el sufijo '_output'
    nodo_retorno_input = p_dic_retornos_input[p_nodo_retorno_output.name.replace(
        '_output', '_input')]
    if (nodo_retorno_input != None):
        p_nodo_retorno_output.max_flow = nodo_retorno_input.max_flow
        p_nodo_retorno_output.cost = nodo_retorno_input.cost
    return(p_nodo_retorno_output)

# Función auxiliar para inicializar los acuiferos
# (9) Acuifero <---> Input [+ Storage]


def InicializarAcuifero_ARTIFICIAL(p_nodo):
    if (p_nodo != None):
        #p_nodo.initial_volume = lstC_ARTIFICIAL_acuifero_init_vol[random.randint(0, len(lstC_ARTIFICIAL_acuifero_init_vol)-1)]
        #p_nodo.min_volume = lstC_ARTIFICIAL_acuifero_min_vol[random.randint(0, len(lstC_ARTIFICIAL_acuifero_min_vol)-1)]
        #p_nodo.max_volume = lstC_ARTIFICIAL_acuifero_max_vol[random.randint(0, len(lstC_ARTIFICIAL_acuifero_max_vol)-1)]
        p_nodo.max_flow = lstC_ARTIFICIAL_acuifero_max_flow[random.randint(
            0, len(lstC_ARTIFICIAL_acuifero_max_flow)-1)]
        p_nodo.cost = lstC_ARTIFICIAL_acuifero_cost[random.randint(
            0, len(lstC_ARTIFICIAL_acuifero_cost)-1)]
    return (p_nodo)


#############################################################################################
# Funciones auxiliares de inicialización de datos de manera REAL, en base a la información
# obtenida desde el archivo SEGU.FIS del modelo SIMGES de Aquatool.
#############################################################################################

# Función auxiliar para inicializar los embalses
# (1) Embalse <---> Storage
def InicializarEmbalse_con_datos_SIMGES(p_embalse, p_df_pdf_embalses, p_intSimulation_step,
                                        p_dic_PARAMS_EMBALSES_vol_min_mensual, p_dic_PARAMS_EMBALSES_vol_max_mensual,
                                        p_dic_PARAMS_EMBALSES_vol_min_diario, p_dic_PARAMS_EMBALSES_vol_max_diario):
    if (p_embalse != None) and (p_df_pdf_embalses.empty == False):

        # Analizemos cada uno de los datos que podemos encontrar en p_df_pdf_embalses ('_pdf_' stands for Phyical Data File)
        # Campo 'prioridad': representa un valor que cuanto mayor es, mayor "coste de embalsado" representa.
        # Entre dos embalses que tienen un volumen / nivel similar, se utilizará antes el agua del embalse que mayor valor
        # de 'prioridad' tenga. Por tanto, es justamente lo opuesto al concepto de 'coste' de pywr.
        # Por tanto, de primeras, como 'prioridad' tiene siempre un valor positivo, podemos mutiplicarlo por (-1)
        # para convetirlo en un coste de pywr.

        # Primero de todo, identificamos el embalse en p_df_pdf_embalses:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_embalse = p_df_pdf_embalses[p_df_pdf_embalses[CFSDE_col_nombre]
                                       == '"' + p_embalse.comment + '"']
        if (df_embalse.shape[0] > 0):

            # Ahora, aplicamos el concepto de coste a la prioridad
            p_embalse.cost = (-1) * df_embalse[CFSDE_col_n_prioridad].values[0]

            # Hay un valor de volumen inicial, por tanto, lo tamamos.
            p_embalse.initial_volume = df_embalse[CFSDE_col_vol_inicial].values[0]

            # Hay un valor de caudal máximo de sueltas controladas que, inicialmente, tomaremos como q max
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_embalse.max_flow = df_embalse[CFSDE_col_q_max_sueltas].values[0]
            else:  # Si el tipo de simulación es SIMULATION_STEP_PASO_DIARIO, se divide q max entre N_DIAS_MES_ESTANDAR
                p_embalse.max_flow = df_embalse[CFSDE_col_q_max_sueltas].values[0] / \
                    N_DIAS_MES_ESTANDAR

            # Para los valores de volumen mínimo y volumen máximo, como estos tienen un valor mensual diferente
            # se han creado unos parámetros que se referencias en unos diccionaros. Usaremos estos parámetros.
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_embalse.min_volume = p_dic_PARAMS_EMBALSES_vol_min_mensual[
                    PARAM_NOMBRE_vol_min_values_MENSUAL + p_embalse.comment]
                p_embalse.max_volume = p_dic_PARAMS_EMBALSES_vol_max_mensual[
                    PARAM_NOMBRE_vol_max_values_MENSUAL + p_embalse.comment]
            else:
                p_embalse.min_volume = p_dic_PARAMS_EMBALSES_vol_min_diario[
                    PARAM_NOMBRE_vol_min_values_DIARIO + p_embalse.comment]
                p_embalse.max_volume = p_dic_PARAMS_EMBALSES_vol_max_diario[
                    PARAM_NOMBRE_vol_max_values_DIARIO + p_embalse.comment]

            # Según un mensaje de error al intentar ejecutar el modelo y según la documentación del elemento
            # 'Storage', cuando max_volume se define en forma de parámetro, es necesario definir tanto 'initial_volume'
            # como 'initial_volume_pc' (percentage).
            # ("RuntimeError: Both 'initial_volume' and 'initial_volume_pc' must be supplied if 'max_volume'
            # is defined as a parameter.")
            # Como este dato no se proporciona desde el archivo de datos físicos SEGU.FIS, lo calcularemos en base
            # al valor máximo del array de valores guardado en el correspondiente parámetro guardado en
            # el diccionario dic_PARAMS_EMBALSES_vol_max_mensual{} y el valor del volumen inicial, que si se proporciona
            # en el archivo de datos físicos SEGU.FIS.
            values_str = df_embalse[CFSDE_col_v_max_mensual_12_vals].values[0]
            values_list = [float(j) for j in values_str.split()]
            p_embalse.initial_volume_pc = min(
                1.0, df_embalse[CFSDE_col_vol_inicial].values[0] / max(values_list))

        else:
            print("WARNING: Función 'InicializarEmbalse_con_datos_SIMGES'; no se ha encontrado el EMBALSE: %s" % (
                p_embalse.comment))

    return (p_embalse)


# Función auxiliar para inicializar las aportaciones
# (2) Aportacion <---> Input
def InicializarAportacion_con_datos_SIMGES(p_aportacion, p_df_pdf_aportaciones, p_intSimulation_step,
                                           p_dic_PARAMS_APORTACIONES_mensual, p_dic_PARAMS_APORTACIONES_diario):
    if (p_aportacion != None) and (p_df_pdf_aportaciones.empty == False):

        # El único dato que hay que cargar, son las series temporales de aportaciones
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_aportacion = p_df_pdf_aportaciones[p_df_pdf_aportaciones[CFSDA_col_nombre]
                                              == '"' + p_aportacion.comment + '"']
        if (df_aportacion.shape[0] > 0):
            # Si el tipo de simulación es SIMULATION_STEP_PASO_MENSUAL, asociamos a max_flow el parámetro que guarda
            # las series temporales de aportaciones mensuales
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_aportacion.max_flow = p_dic_PARAMS_APORTACIONES_mensual[
                    PARAM_NOMBRE_aportaciones_MENSUAL + p_aportacion.comment]
            else:  # Si el tipo de simulación es SIMULATION_STEP_PASO_DIARIO, se asocia el parámetro que guarda
                # las series temporales de aportaciones diarias
                p_aportacion.max_flow = p_dic_PARAMS_APORTACIONES_diario[
                    PARAM_NOMBRE_aportaciones_DIARIO + p_aportacion.comment]

        else:
            print("WARNING: Función 'InicializarAportacion_con_datos_SIMGES'; no se ha encontrado la APORTACION: %s" % (
                p_aportacion.comment))

    return (p_aportacion)


# Función auxiliar para inicializar las demandas
# (3) Demanda <---> Output
def InicializarDemanda_con_datos_SIMGES(p_demanda, p_df_pdf_demandas, p_intSimulation_step,
                                        p_dic_PARAMS_DEMANDAS_mensual, p_dic_PARAMS_DEMANDAS_diario):
    if (p_demanda != None) and (p_df_pdf_demandas.empty == False):

        # Analizemos cada uno de los datos que podemos encontrar en p_df_pdf_demandas ('_pdf_' stands for Phyical Data File)

        # Primero de todo, identificamos la demanda en p_df_pdf_demandas:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_demanda = p_df_pdf_demandas[p_df_pdf_demandas[CFSDD_col_nombre]
                                       == '"' + p_demanda.comment + '"']
        if (df_demanda.shape[0] > 0):

            # Para los valores de caudal de demanda, como estos tienen un valor mensual diferente
            # se han creado unos parámetros que se referencias en unos diccionaros. Usaremos estos parámetros.
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_demanda.max_flow = p_dic_PARAMS_DEMANDAS_mensual[
                    PARAM_NOMBRE_demanda_values_MENSUAL + p_demanda.comment]
            else:
                p_demanda.max_flow = p_dic_PARAMS_DEMANDAS_diario[
                    PARAM_NOMBRE_demanda_values_DIARIO + p_demanda.comment]

        else:
            print("WARNING: Función 'InicializarDemanda_con_datos_SIMGES'; no se ha encontrado la DEMANDA: %s" % (
                p_demanda.comment))

    return (p_demanda)


# Función auxiliar para inicializar las tomas
# (4) Toma <---> MultiSplitLink
def InicializarToma_con_datos_SIMGES(p_toma, p_df_pdf_demandas, p_intSimulation_step):
    if (p_toma != None) and (p_df_pdf_demandas.empty == False):

        # Lo que tenemos que hacer, es en contrar la toma en las columnas de 5 posibles tomas que tienen las demandas,
        # y una vez encontrada la toma, asignarle sus coeficientes de consumo y de retorno:
        for j in range(CFSDD_max_n_tomas):
            # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
            #             al imprincipio y al final.
            df_toma = p_df_pdf_demandas[p_df_pdf_demandas[CFSDD_col_nombre_toma + '_' + str(
                j+1)] == '"' + p_toma.comment + '"']
            if (df_toma.shape[0] > 0):  # Se ha encontrado la toma
                # Ahora, obtener el coeficiente de retorno y el coeficiente de consumo, y establecer esos valores en la toma:
                factor_retorno = df_toma[CFSDD_col_coef_retorno +
                                         '_' + str(j+1)].values[0]
                factor_demanda = df_toma[CFSDD_col_coef_consumo +
                                         '_' + str(j+1)].values[0]
                p_toma.factors = [factor_demanda, factor_retorno]

                break  # Finish outer for loop

    # Si no se ha encontrado la toma, mostrar mensaje.
    if (j >= CFSDD_max_n_tomas):
        print("WARNING: Función 'InicializarToma_con_datos_SIMGES'; no se ha encontrado la TOMA: %s" % (
            p_toma.comment))
    return (p_toma)


# Función auxiliar para inicializar las conducciones1
# (5) Conduccion1 <---> LossLink
def InicializarConduccion1_con_datos_SIMGES(p_conduccion1, p_df_pdf_conducciones1, p_intSimulation_step,
                                            p_dic_PARAMS_CONDUCCIONES1_q_min_mensual, p_dic_PARAMS_CONDUCCIONES1_q_max_mensual,
                                            p_dic_PARAMS_CONDUCCIONES1_q_min_diario, p_dic_PARAMS_CONDUCCIONES1_q_max_diario):
    if (p_conduccion1 != None) and (p_df_pdf_conducciones1.empty == False):

        # Analizemos cada uno de los datos que podemos encontrar en p_df_pdf_conducciones1 ('_pdf_' stands for Phyical Data File)

        # Primero de todo, identificamos la conduccion1 en p_df_pdf_conducciones1:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_conduccion1 = p_df_pdf_conducciones1[p_df_pdf_conducciones1[CFSDC1_col_nombre]
                                                == '"' + p_conduccion1.comment + '"']
        if (df_conduccion1.shape[0] > 0):

            # Para los valores de caudal mínimo y caudal máximo, como estos tienen un valor mensual diferente
            # se han creado unos parámetros que se referencias en unos diccionaros. Usaremos estos parámetros.
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_conduccion1.min_flow = p_dic_PARAMS_CONDUCCIONES1_q_min_mensual[
                    PARAM_NOMBRE_q_min_values_MENSUAL + p_conduccion1.comment]
                p_conduccion1.max_flow = p_dic_PARAMS_CONDUCCIONES1_q_max_mensual[
                    PARAM_NOMBRE_q_max_values_MENSUAL + p_conduccion1.comment]
            else:
                p_conduccion1.min_flow = p_dic_PARAMS_CONDUCCIONES1_q_min_diario[
                    PARAM_NOMBRE_q_min_values_DIARIO + p_conduccion1.comment]
                p_conduccion1.max_flow = p_dic_PARAMS_CONDUCCIONES1_q_max_diario[
                    PARAM_NOMBRE_q_max_values_DIARIO + p_conduccion1.comment]

        else:
            print("WARNING: Función 'InicializarConduccion1_con_datos_SIMGES'; no se ha encontrado la CONDUCCION1: %s" % (
                p_conduccion1.comment))

    return (p_conduccion1)


# Función auxiliar para inicializar las conducciones3
# (6) Conduccion3 <---> LossLink
def InicializarConduccion3_con_datos_SIMGES(p_conduccion3, p_df_pdf_conducciones3, p_intSimulation_step,
                                            p_dic_PARAMS_CONDUCCIONES3_q_min_mensual, p_dic_PARAMS_CONDUCCIONES3_q_max_mensual,
                                            p_dic_PARAMS_CONDUCCIONES3_q_min_diario, p_dic_PARAMS_CONDUCCIONES3_q_max_diario):
    if (p_conduccion3 != None) and (p_df_pdf_conducciones3.empty == False):

        # Analizemos cada uno de los datos que podemos encontrar en p_df_pdf_conducciones3 ('_pdf_' stands for Phyical Data File)

        # Primero de todo, identificamos la conduccion3 en p_df_pdf_conducciones3:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_conduccion3 = p_df_pdf_conducciones3[p_df_pdf_conducciones3[CFSDC3_col_nombre]
                                                == '"' + p_conduccion3.comment + '"']
        if (df_conduccion3.shape[0] > 0):

            # Para los valores de caudal mínimo y caudal máximo, como estos tienen un valor mensual diferente
            # se han creado unos parámetros que se referencias en unos diccionaros. Usaremos estos parámetros.
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_conduccion3.min_flow = p_dic_PARAMS_CONDUCCIONES3_q_min_mensual[
                    PARAM_NOMBRE_q_min_values_MENSUAL + p_conduccion3.comment]
                p_conduccion3.max_flow = p_dic_PARAMS_CONDUCCIONES3_q_max_mensual[
                    PARAM_NOMBRE_q_max_values_MENSUAL + p_conduccion3.comment]
            else:
                p_conduccion3.min_flow = p_dic_PARAMS_CONDUCCIONES3_q_min_diario[
                    PARAM_NOMBRE_q_min_values_DIARIO + p_conduccion3.comment]
                p_conduccion3.max_flow = p_dic_PARAMS_CONDUCCIONES3_q_max_diario[
                    PARAM_NOMBRE_q_max_values_DIARIO + p_conduccion3.comment]

        else:
            print("WARNING: Función 'InicializarConduccion3_con_datos_SIMGES'; no se ha encontrado la CONDUCCION3: %s" % (
                p_conduccion3.comment))

    return (p_conduccion3)


# Función auxiliar para inicializar los bombeos
# (7) Bombeo <---> Link
def InicializarBombeo_con_datos_SIMGES(p_bombeo, p_df_pdf_bombeos, p_intSimulation_step):
    if (p_bombeo != None) and (p_df_pdf_bombeos.empty == False):

        # Analizemos cada uno de los datos que podemos encontrar en p_df_pdf_bombeos ('_pdf_' stands for Phyical Data File)

        # Primero de todo, identificamos el bombeo en p_df_pdf_bombeos:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_bombeo = p_df_pdf_bombeos[p_df_pdf_bombeos[CFSDB_col_nombre]
                                     == '"' + p_bombeo.comment + '"']
        if (df_bombeo.shape[0] > 0):

            # Hay un valor de caudal máximo de bombeo
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_bombeo.max_flow = df_bombeo[CFSDB_col_q_maximo_mensual_a_bombear].values[0]
            else:  # Si el tipo de simulación es SIMULATION_STEP_PASO_DIARIO, se divide q max entre N_DIAS_MES_ESTANDAR
                p_bombeo.max_flow = df_bombeo[CFSDB_col_q_maximo_mensual_a_bombear].values[0] / \
                    N_DIAS_MES_ESTANDAR

        else:
            print("WARNING: Función 'InicializarBombeo_con_datos_SIMGES'; no se ha encontrado el BOMBEO: %s" % (
                p_bombeo.comment))

    return (p_bombeo)


# Función auxiliar para inicializar los retornos
# (8) Retorno <---> Input + Output
# Parte Input
# NOTA: por el momento, como los retornos no están conectados y en SIMGES no se define ninguna serie temporal,
# asumimos que tienen un valor de max_flow = 0.
# Aunque los retornos son de todo tipo y por tanto los costes deberían ser también de diferentes tipos,
# por el momento los ponemos a 0 porque max_flow = 0.
def InicializarRetorno_Input_con_datos_SIMGES(p_retorno_input):
    if (p_retorno_input != None):
        p_retorno_input.max_flow = 0
        p_retorno_input.cost = 0
    return (p_retorno_input)


# Función auxiliar para inicializar los retornos
# (8) Retorno <---> Input + Output
# Parte Output
def InicializarRetorno_Output_con_datos_SIMGES(p_retorno_output, p_df_pdf_retornos, p_intSimulation_step,
                                               p_dic_PARAMS_RETORNOS_demanda_mensual, p_dic_PARAMS_RETORNOS_demanda_diario):

    if (p_retorno_output != None) and (p_df_pdf_retornos.empty == False):
        # Primero de todo, identificamos el retorno_output en p_df_pdf_retornos:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_retorno_output = p_df_pdf_retornos[p_df_pdf_retornos[CFSDR_col_nombre]
                                              == '"' + p_retorno_output.comment + '"']
        if (df_retorno_output.shape[0] > 0):

            # Primero de todo, establecemos que el coste es 0
            p_retorno_output.cost = 0

            # Para los valores de volumen de recarga, como estos tienen un valor mensual diferente
            # se han creado unos parámetros que se referencias en unos diccionaros. Usaremos estos parámetros.
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                p_retorno_output.max_flow = p_dic_PARAMS_RETORNOS_demanda_mensual[
                    PARAM_NOMBRE_demanda_retorno_values_MENSUAL + p_retorno_output.comment]
            else:
                p_retorno_output.max_flow = p_dic_PARAMS_RETORNOS_demanda_diario[
                    PARAM_NOMBRE_demanda_retorno_values_DIARIO + p_retorno_output.comment]

        else:
            print("WARNING: Función 'InicializarRetorno_Output_con_datos_SIMGES'; no se ha encontrado el RETORNO: %s" % (
                p_retorno_output.comment))

    return (p_retorno_output)

# Función que iguala los valores de inicialización de retorno_input con respecto a retorno_output


def IgualarValoresInicializacionRetornos_con_datos_SIMGES(p_retorno_output, p_dic_retornos_input):

    # IMPORTANTE: recordar que el ID del retorno en dic_retornos_input tiene el sufijo '_input' y en dic_retornos_output
    #             el sufijo '_output'
    nodo_retorno_input = p_dic_retornos_input[p_retorno_output.name.replace(
        '_output', '_input')]
    if (nodo_retorno_input != None):
        nodo_retorno_input.max_flow = p_retorno_output.max_flow
        nodo_retorno_input.cost = p_retorno_output.cost
    return(p_retorno_output)


# Función auxiliar para inicializar los acuiferos
# (9) Acuifero <---> Input
def InicializarAcuifero_con_datos_SIMGES(p_acuifero, p_df_pdf_acuiferos, p_intSimulation_step,
                                         p_dic_PARAMS_ACUIFEROS_recarga_mensual, p_dic_PARAMS_ACUIFEROS_recarga_diario):
    if (p_acuifero != None) and (p_df_pdf_acuiferos.empty == False):

        # Primero de todo, identificamos el acuifero en p_df_pdf_acuiferos:
        # IMPORTANTE: recordar que los nombres de los elementos en el archivo de datos físicos tienen siempre doble comilla (")
        #             al imprincipio y al final.
        df_acuifero = p_df_pdf_acuiferos[p_df_pdf_acuiferos[CFSDAC_col_nombre]
                                         == '"' + p_acuifero.comment + '"']
        if (df_acuifero.shape[0] > 0):

            # Hay un valor de volumen inicial, por tanto, lo tamamos.
            p_acuifero.initial_volume = df_acuifero[CFSDAC_col_volumen_inicial].values[0]

            # Para los valores de volumen de recarga, como estos tienen un valor mensual diferente
            # se han creado unos parámetros que se referencias en unos diccionaros. Usaremos estos parámetros.
            if (p_intSimulation_step == SIMULATION_STEP_PASO_MENSUAL):
                #                p_acuifero.max_volume = dic_PARAMS_ACUIFEROS_recarga_mensual[PARAM_NOMBRE_recarga_acuifero_values_MENSUAL + p_acuifero.comment]
                p_acuifero.max_flow = p_dic_PARAMS_ACUIFEROS_recarga_mensual[
                    PARAM_NOMBRE_recarga_acuifero_values_MENSUAL + p_acuifero.comment]
            else:
                #                p_acuifero.max_volume = dic_PARAMS_ACUIFEROS_recarga_diario[PARAM_NOMBRE_recarga_acuifero_values_DIARIO + p_acuifero.comment]
                p_acuifero.max_flow = p_dic_PARAMS_ACUIFEROS_recarga_diario[
                    PARAM_NOMBRE_recarga_acuifero_values_DIARIO + p_acuifero.comment]

        else:
            print("WARNING: Función 'InicializarAcuifero_con_datos_SIMGES'; no se ha encontrado el ACUIFERO: %s" % (
                p_acuifero.comment))

    return (p_acuifero)


#######################
# MAIN FUNCTION	      #
#######################


# ******************************************************************************************************
# FUNCTION: Planificar_Optimizar_Suministros_a_Demandas(p_simulation_type, p_simulation_step, p_date_init, p_date_end, \
#                                                       p_percent_agua_superficial=1.0, p_percent_agua_subterranea=1.0, \
#                                                       p_percent_agua_reutilizada=1.0, p_percent_agua_trasvase=1.0, \
#                                                       p_percent_agua_desalada=1.0, \
#                                                       p_peso_deficit=1.0, p_peso_co2=0.0, p_peso_economic=0.0)
#
# DESCRIPTION: Realizar la planificación u optimización de suministros a demandas de la CHS.
# ARGUMENTS:
# 	p_simulation_type: valor entero que indica si es PLANIFICACION (1) u OPTIMIZACION (2)
#	p_simulation_step: valor entero que indica si es DIARIO (1) o MENSUAL (2)
# 	p_date_init: string de fecha de inicio de simulación en formato '%Y-%m-%d'
# 	p_date_end: string de fecha de fin de simulación en formato '%Y-%m-%d'
#   p_percent_agua_superficial: % que el usuario define y que debe aplicarse sobre el agua superficial disponible. Se trata de un valor
#                               limitado a 0.5 por debajo y a 1.5 por arriba, lo que representa utilizar desde un mínimo del 50%
#                               hasta un máximo del 150% de agua superficial disponible.
#   p_percent_agua_subterranea: % que el usuario define y que debe aplicarse sobre el agua superficial disponible. Se trata de un valor
#                               limitado a 0.5 por debajo y a 1.5 por arriba, lo que representa utilizar desde un mínimo del 50%
#                               hasta un máximo del 150% de agua superficial disponible.
#   p_percent_agua_reutilizada: % que el usuario define y que debe aplicarse sobre el agua superficial disponible. Se trata de un valor
#                               limitado a 0.5 por debajo y a 1.5 por arriba, lo que representa utilizar desde un mínimo del 50%
#                               hasta un máximo del 150% de agua superficial disponible.
#   p_percent_agua_trasvase:    % que el usuario define y que debe aplicarse sobre el agua superficial disponible. Se trata de un valor
#                               limitado a 0.5 por debajo y a 1.5 por arriba, lo que representa utilizar desde un mínimo del 50%
#                               hasta un máximo del 150% de agua superficial disponible.
#   p_percent_agua_desalada:    % que el usuario define y que debe aplicarse sobre el agua superficial disponible. Se trata de un valor
#                               limitado a 0.5 por debajo y a 1.5 por arriba, lo que representa utilizar desde un mínimo del 50%
#                               hasta un máximo del 150% de agua superficial disponible.
#   p_weight_deficit:  valor real (float) entre 0.0 y 1.0. Representa el peso / la importancia que se le da a la minimización del déficit
#                      en la función de optimización de pywr. Debe cumplirse la restricción de que la suma de p_peso_deficit, p_peso_co2 y
#                      p_peso_economic debe ser 1.0.
#   p_weight_co2:      valor real (float) entre 0.0 y 1.0. Representa el peso / la importancia que se le da a la minimización del co2
#                      en la función de optimización de pywr. Debe cumplirse la restricción de que la suma de p_peso_deficit, p_peso_co2 y
#                      p_peso_economic debe ser 1.0.
#   p_weight_economic: valor real (float) entre 0.0 y 1.0. Representa el peso / la importancia que se le da a la maximización del balance
#                      económico en la función de optimización de pywr. Debe cumplirse la restricción de que la suma de p_peso_deficit,
#                      p_peso_co2 y p_peso_economic debe ser 1.0.
#
# ******************************************************************************************************
def Planificar_Optimizar_Suministros_a_Demandas(p_simulation_type, p_simulation_step, p_date_init, p_date_end,
                                                p_percent_agua_superficial=1.0, p_percent_agua_subterranea=1.0,
                                                p_percent_agua_reutilizada=1.0, p_percent_agua_trasvase=1.0,
                                                p_percent_agua_desalada=1.0,
                                                p_peso_deficit=1.0, p_peso_co2=0.0, p_peso_economic=0.0):

    # 1. First, open config and input files

    # 1.1 Open CONFIG FILES file
    xl_cf = pd.ExcelFile(CONFIG_FILE)

    # 1.2.1 Get config data for file 'IN_tpa_to_dataframe_file'
    df_config_tpatdff = xl_cf.parse(
        sheet_name=CF_SHEET_IN_FILE_tpa_dataframe_file, header=CFSIFtdf_HEADER)

    # 1.2.2 Open IN_tpa_to_dataframe_file_path, that is, TPA TO DATAFRAME FILE (HYDROLOGICAL NETWORK FILE)
    xl_tpatdff = pd.ExcelFile(
        df_config_tpatdff[CFSIFtdf_input_file_path].iloc[0])
    df_tpatdff = xl_tpatdff.parse(
        sheet_name=df_config_tpatdff[CFSIFtdf_sheet].iloc[0], header=df_config_tpatdff[CFSIFtdf_header].iloc[0])

    # 1.3.1 Get config data for file 'IN_physical_data_file'
    df_config_pdf = xl_cf.parse(
        sheet_name=CF_SHEET_IN_FILE_physical_data_file, header=CFSIFpdf_HEADER)

    # 1.3.2 Open IN_physical_data_file_path (phsycical data and elements' initialisation data file)
    xl_pdf = pd.ExcelFile(
        df_config_pdf[CFSIFpdf_physical_data_file_path].iloc[0])

    # (1) General data
    df_pdf = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_datos_generales].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # (2) Elements data

    # Embalses
    df_pdf_embalses = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_embalses].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Aportaciones
    df_pdf_aportaciones = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_aportaciones].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Demandas
    df_pdf_demandas = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_demandas].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Conducciones1
    df_pdf_conducciones1 = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_conducciones1].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Conducciones3
    df_pdf_conducciones3 = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_conducciones3].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Acuiferos
    df_pdf_acuiferos = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_acuiferos].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Bombeos
    df_pdf_bombeos = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_bombeos].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # Retornos
    df_pdf_retornos = xl_pdf.parse(
        sheet_name=df_config_pdf[CFSIFpdf_sheet_retornos].iloc[0], header=df_config_pdf[CFSIFpdf_header_general].iloc[0])

    # 2. Now, we start to create the hydrological model

    # 2.1 create a model (including an empty network)
    model = Model()

    ################################
    # Create the needed parameters
    ################################

    # (1) Parámetros para embalses (mensual)
    # Crear diccionario de parámetros de volumen mínimo mensual para embalses
    dic_PARAMS_EMBALSES_vol_min_mensual = {}
    # Crear diccionario de parámetros de volumen máximo mensual para embalses
    dic_PARAMS_EMBALSES_vol_max_mensual = {}

    # Parámetros para embalses (diario)
    # Crear diccionario de parámetros de volumen mínimo diario para embalses
    dic_PARAMS_EMBALSES_vol_min_diario = {}
    # Crear diccionario de parámetros de volumen máximo diario para embalses
    dic_PARAMS_EMBALSES_vol_max_diario = {}

    # Run for loop
    for i in range(df_pdf_embalses.shape[0]):
        # Determinamos el nombre del embalse
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_embalse = df_pdf_embalses[CFSDE_col_nombre].iloc[i].replace(
            '"', '')

        # (1.1) Empezamos con los parámetros de volumen mínimo mensual para embalses:
        values_str_mensual = df_pdf_embalses[CFSDE_col_v_min_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_vol_min_values_MENSUAL + nombre_embalse
        dic_PARAMS_EMBALSES_vol_min_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual, columns=[nombre_embalse])
        if (i == 0):
            df_PARAMS_EMBALSES_vol_min_mensual = df_temp
        else:
            df_PARAMS_EMBALSES_vol_min_mensual = pd.concat([df_PARAMS_EMBALSES_vol_min_mensual.reset_index(drop=True),
                                                            df_temp.reset_index(drop=True)], axis=1)

        # (1.2) Lo replicamos para el paso diario
        # NOTA importante sobre "DailyProfileParameter":
        # "An annual profile consisting of daily values.
        # This parameter provides a repeating annual profile with a daily resolution.
        # A total of 366 values must be provided. These values are coerced to a numpy.array internally."
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
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_vol_min_values_DIARIO + nombre_embalse
        dic_PARAMS_EMBALSES_vol_min_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[nombre_embalse])
        if (i == 0):
            df_PARAMS_EMBALSES_vol_min_diario = df_temp
        else:
            df_PARAMS_EMBALSES_vol_min_diario = pd.concat([df_PARAMS_EMBALSES_vol_min_diario.reset_index(drop=True),
                                                           df_temp.reset_index(drop=True)], axis=1)

        # (2.1) Seguimos con los parámetros de volumen máximo mensual para embalses:
        values_str_mensual = df_pdf_embalses[CFSDE_col_v_max_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_vol_max_values_MENSUAL + nombre_embalse
        dic_PARAMS_EMBALSES_vol_max_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual, columns=[nombre_embalse])
        if (i == 0):
            df_PARAMS_EMBALSES_vol_max_mensual = df_temp
        else:
            df_PARAMS_EMBALSES_vol_max_mensual = pd.concat([df_PARAMS_EMBALSES_vol_max_mensual.reset_index(drop=True),
                                                            df_temp.reset_index(drop=True)], axis=1)

        # (2.2) Lo replicamos para el paso diario
        for j in range(len(values_list_mensual)):
            if (((j+1) % 2) == 1):
                valores_diarios_temp = [values_list_mensual[j]/31] * 31
            else:
                valores_diarios_temp = [values_list_mensual[j]/30] * 30
            if (j == 0):
                values_list_diario = valores_diarios_temp
            else:
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_vol_max_values_DIARIO + nombre_embalse
        dic_PARAMS_EMBALSES_vol_max_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[nombre_embalse])
        if (i == 0):
            df_PARAMS_EMBALSES_vol_max_diario = df_temp
        else:
            df_PARAMS_EMBALSES_vol_max_diario = pd.concat([df_PARAMS_EMBALSES_vol_max_diario.reset_index(drop=True),
                                                           df_temp.reset_index(drop=True)], axis=1)

    # (2) Tablas (para parámetros) y parámetros para aportaciones (mensual)
    # Crear diccionario de tablas (para parámetros) de aportaciones mensual
    dic_TABLAS_APORTACIONES_mensual = {}
    # Crear diccionario de parámetros de aportaciones mensual
    dic_PARAMS_APORTACIONES_mensual = {}

    # Tablas (para parámetros) y parámetros para aportaciones (diario)
    # Crear diccionario de tablas (para parámetros) de aportaciones kdiario
    dic_TABLAS_APORTACIONES_diario = {}
    # Crear diccionario de parámetros de aportaciones diario
    dic_PARAMS_APORTACIONES_diario = {}

    # Run for loop
    for i in range(df_pdf_aportaciones.shape[0]):
        # Determinamos el nombre de la aportación
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_aportacion = df_pdf_aportaciones[CFSDA_col_nombre].iloc[i].replace(
            '"', '')

        # Determinamos la columna en el archivo de aportaciones
        columna_en_archivo_aportaciones = df_pdf_aportaciones[
            CFSDA_col_columna_en_archivo_aportaciones].iloc[i]

        # (1.1) Empezamos con los parametros de aportaciones mensual:
        file_name_aportaciones = PARAMETROS_APORTACIONES_DIRECTORIO_MENSUAL + PREFIJO_ARCHIVO_CSV_APORTACIONES_MENSUAL + \
            str(columna_en_archivo_aportaciones) + '.csv'

        # Primero, cargamos la tabla con el archivo de la serie temporal haciendo uso del método parameters.load_dataframe()
        # NOTA: en vez de cargar el archivo de la serie temporal directamente como parámetro, se carga como tabla porque
        # de esta manera los datos se cargan una sola vez (como parámetro no), y por tanto la gestión de la memoria es mucho
        # más eficiente.
        datos_tabla = {
            "url": file_name_aportaciones,
            "index_col": ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA,
            "column": ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR,
            "parse_dates": True}
        tabla = load_dataframe(model, datos_tabla)
        nombre_tabla = TABLA_NOMBRE_aportaciones_MENSUAL + nombre_aportacion
        model.tables[nombre_tabla] = tabla
        tabla.name = nombre_tabla
        dic_TABLAS_APORTACIONES_mensual[tabla.name] = tabla

        # A continuación, cargamos el parámetro de tipo "dataframe" haciendo uso del método parameters.load_parameter()
        # y haciendo referencia a la tabla justo creada
        datos_parametro = {
            "name": PARAM_NOMBRE_aportaciones_MENSUAL + nombre_aportacion,
            "type": "dataframe",
            "table": tabla.name}
        parametro = load_parameter(model, datos_parametro)
        dic_PARAMS_APORTACIONES_mensual[parametro.name] = parametro

        # (1.2) Seguimos con los parametros de aportaciones diario:
        file_name_aportaciones = PARAMETROS_APORTACIONES_DIRECTORIO_DIARIO + PREFIJO_ARCHIVO_CSV_APORTACIONES_DIARIO + \
            str(columna_en_archivo_aportaciones) + '.csv'

        # Primero, cargamos la tabla con el archivo de la serie temporal haciendo uso del método parameters.load_dataframe()
        # NOTA: en vez de cargar el archivo de la serie temporal directamente como parámetro, se carga como tabla porque
        # de esta manera los datos se cargan una sola vez (como parámetro no), y por tanto la gestión de la memoria es mucho
        # más eficiente.
        datos_tabla = {
            "url": file_name_aportaciones,
            "index_col": ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA,
            "parse_dates": True,
            "column": ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR}
        tabla = load_dataframe(model, datos_tabla)
        nombre_tabla = TABLA_NOMBRE_aportaciones_DIARIO + nombre_aportacion
        model.tables[nombre_tabla] = tabla
        tabla.name = nombre_tabla
        dic_TABLAS_APORTACIONES_diario[tabla.name] = tabla

        # A continuación, cargamos el parámetro de tipo "dataframe" haciendo uso del método parameters.load_parameter()
        # y haciendo referencia a la tabla justo creada
        datos_parametro = {
            "name": PARAM_NOMBRE_aportaciones_DIARIO + nombre_aportacion,
            "type": "dataframe",
            "table": tabla.name}
        parametro = load_parameter(model, datos_parametro)
        dic_PARAMS_APORTACIONES_diario[parametro.name] = parametro

    # (3) Parámetros para demandas (mensual)
    # Crear diccionario de parámetros de caudal mensual para demandas
    dic_PARAMS_DEMANDAS_mensual = {}

    # Parámetros para demandas (diario)
    # Crear diccionario de parámetros de caudal diario para demandas
    dic_PARAMS_DEMANDAS_diario = {}

    # Run for loop
    for i in range(df_pdf_demandas.shape[0]):
        # Determinamos el nombre de la demanda
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_demanda = df_pdf_demandas[CFSDD_col_nombre].iloc[i].replace(
            '"', '')

        # (1.1) Empezamos con los parámetros de caudal de demanda mensual para demandas:
        values_str_mensual = df_pdf_demandas[CFSDD_col_demanda_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_demanda_values_MENSUAL + nombre_demanda
        dic_PARAMS_DEMANDAS_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual, columns=[nombre_demanda])
        if (i == 0):
            df_PARAMS_DEMANDAS_mensual = df_temp
        else:
            df_PARAMS_DEMANDAS_mensual = pd.concat([df_PARAMS_DEMANDAS_mensual.reset_index(drop=True),
                                                    df_temp.reset_index(drop=True)], axis=1)

        # (1.2) Lo replicamos para el paso diario
        # NOTA importante sobre "DailyProfileParameter":
        # "An annual profile consisting of daily values.
        # This parameter provides a repeating annual profile with a daily resolution.
        # A total of 366 values must be provided. These values are coerced to a numpy.array internally."
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
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_demanda_values_DIARIO + nombre_demanda
        dic_PARAMS_DEMANDAS_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[nombre_demanda])
        if (i == 0):
            df_PARAMS_DEMANDAS_diario = df_temp
        else:
            df_PARAMS_DEMANDAS_diario = pd.concat([df_PARAMS_DEMANDAS_diario.reset_index(drop=True),
                                                   df_temp.reset_index(drop=True)], axis=1)

    # (5) Parámetros para conducciones1 (mensual)
    # Crear diccionario de parámetros de caudal mínimo mensual para conducciones1
    dic_PARAMS_CONDUCCIONES1_q_min_mensual = {}
    # Crear diccionario de parámetros de caudal máximo mensual para conducciones1
    dic_PARAMS_CONDUCCIONES1_q_max_mensual = {}

    # Parámetros para conducciones1 (diario)
    # Crear diccionario de parámetros de caudal mínimo diario para conducciones1
    dic_PARAMS_CONDUCCIONES1_q_min_diario = {}
    # Crear diccionario de parámetros de caudal máximo diario para conducciones1
    dic_PARAMS_CONDUCCIONES1_q_max_diario = {}

    # Run for loop
    for i in range(df_pdf_conducciones1.shape[0]):
        # Determinamos el nombre de la conduccion1
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_conduccion1 = df_pdf_conducciones1[CFSDC1_col_nombre].iloc[i].replace(
            '"', '')

        # (1.1) Empezamos con los parámetros de caudal mínimo mensual para conducciones1:
        values_str_mensual = df_pdf_conducciones1[CFSDC1_col_qmin_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_q_min_values_MENSUAL + nombre_conduccion1
        dic_PARAMS_CONDUCCIONES1_q_min_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual,
                               columns=[nombre_conduccion1])
        if (i == 0):
            df_PARAMS_CONDUCCIONES1_q_min_mensual = df_temp
        else:
            df_PARAMS_CONDUCCIONES1_q_min_mensual = pd.concat([df_PARAMS_CONDUCCIONES1_q_min_mensual.reset_index(drop=True),
                                                               df_temp.reset_index(drop=True)], axis=1)

        # (1.2) Lo replicamos para el paso diario
        # NOTA importante sobre "DailyProfileParameter":
        # "An annual profile consisting of daily values.
        # This parameter provides a repeating annual profile with a daily resolution.
        # A total of 366 values must be provided. These values are coerced to a numpy.array internally."
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
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_q_min_values_DIARIO + nombre_conduccion1
        dic_PARAMS_CONDUCCIONES1_q_min_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[
                               nombre_conduccion1])
        if (i == 0):
            df_PARAMS_CONDUCCIONES1_q_min_diario = df_temp
        else:
            df_PARAMS_CONDUCCIONES1_q_min_diario = pd.concat([df_PARAMS_CONDUCCIONES1_q_min_diario.reset_index(drop=True),
                                                              df_temp.reset_index(drop=True)], axis=1)

        # (2.1) Seguimos con los parámetros de caudal máximo mensual para conducciones1:
        values_str_mensual = df_pdf_conducciones1[CFSDC1_col_qmax_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_q_max_values_MENSUAL + nombre_conduccion1
        dic_PARAMS_CONDUCCIONES1_q_max_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual,
                               columns=[nombre_conduccion1])
        if (i == 0):
            df_PARAMS_CONDUCCIONES1_q_max_mensual = df_temp
        else:
            df_PARAMS_CONDUCCIONES1_q_max_mensual = pd.concat([df_PARAMS_CONDUCCIONES1_q_max_mensual.reset_index(drop=True),
                                                               df_temp.reset_index(drop=True)], axis=1)

        # (2.2) Lo replicamos para el paso diario
        for j in range(len(values_list_mensual)):
            if (((j+1) % 2) == 1):
                valores_diarios_temp = [values_list_mensual[j]/31] * 31
            else:
                valores_diarios_temp = [values_list_mensual[j]/30] * 30
            if (j == 0):
                values_list_diario = valores_diarios_temp
            else:
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_q_max_values_DIARIO + nombre_conduccion1
        dic_PARAMS_CONDUCCIONES1_q_max_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[
                               nombre_conduccion1])
        if (i == 0):
            df_PARAMS_CONDUCCIONES1_q_max_diario = df_temp
        else:
            df_PARAMS_CONDUCCIONES1_q_max_diario = pd.concat([df_PARAMS_CONDUCCIONES1_q_max_diario.reset_index(drop=True),
                                                              df_temp.reset_index(drop=True)], axis=1)

    # (6) Parámetros para conducciones3 (mensual)
    # Crear diccionario de parámetros de caudal mínimo mensual para conducciones3
    dic_PARAMS_CONDUCCIONES3_q_min_mensual = {}
    # Crear diccionario de parámetros de caudal máximo mensual para conducciones3
    dic_PARAMS_CONDUCCIONES3_q_max_mensual = {}

    # Parámetros para conducciones3 (diario)
    # Crear diccionario de parámetros de caudal mínimo diario para conducciones3
    dic_PARAMS_CONDUCCIONES3_q_min_diario = {}
    # Crear diccionario de parámetros de caudal máximo diario para conducciones3
    dic_PARAMS_CONDUCCIONES3_q_max_diario = {}

    # Run for loop
    for i in range(df_pdf_conducciones3.shape[0]):
        # Determinamos el nombre de la conduccion3
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_conduccion3 = df_pdf_conducciones3[CFSDC3_col_nombre].iloc[i].replace(
            '"', '')

        # (1.1) Empezamos con los parámetros de caudal mínimo mensual para conducciones3:
        values_str_mensual = df_pdf_conducciones3[CFSDC3_col_qmin_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_q_min_values_MENSUAL + nombre_conduccion3
        dic_PARAMS_CONDUCCIONES3_q_min_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual,
                               columns=[nombre_conduccion3])
        if (i == 0):
            df_PARAMS_CONDUCCIONES3_q_min_mensual = df_temp
        else:
            df_PARAMS_CONDUCCIONES3_q_min_mensual = pd.concat([df_PARAMS_CONDUCCIONES3_q_min_mensual.reset_index(drop=True),
                                                               df_temp.reset_index(drop=True)], axis=1)

        # (1.2) Lo replicamos para el paso diario
        # NOTA importante sobre "DailyProfileParameter":
        # "An annual profile consisting of daily values.
        # This parameter provides a repeating annual profile with a daily resolution.
        # A total of 366 values must be provided. These values are coerced to a numpy.array internally."
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
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_q_min_values_DIARIO + nombre_conduccion3
        dic_PARAMS_CONDUCCIONES3_q_min_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[
                               nombre_conduccion3])
        if (i == 0):
            df_PARAMS_CONDUCCIONES3_q_min_diario = df_temp
        else:
            df_PARAMS_CONDUCCIONES3_q_min_diario = pd.concat([df_PARAMS_CONDUCCIONES3_q_min_diario.reset_index(drop=True),
                                                              df_temp.reset_index(drop=True)], axis=1)

        # (2.1) Seguimos con los parámetros de caudal máximo mensual para conducciones3:
        values_str_mensual = df_pdf_conducciones3[CFSDC3_col_qmax_mensual_12_vals].iloc[i]
        values_list_mensual = [float(j) for j in values_str_mensual.split()]
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_q_max_values_MENSUAL + nombre_conduccion3
        dic_PARAMS_CONDUCCIONES3_q_max_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual,
                               columns=[nombre_conduccion3])
        if (i == 0):
            df_PARAMS_CONDUCCIONES3_q_max_mensual = df_temp
        else:
            df_PARAMS_CONDUCCIONES3_q_max_mensual = pd.concat([df_PARAMS_CONDUCCIONES3_q_max_mensual.reset_index(drop=True),
                                                               df_temp.reset_index(drop=True)], axis=1)

        # (2.2) Lo replicamos para el paso diario
        for j in range(len(values_list_mensual)):
            if (((j+1) % 2) == 1):
                valores_diarios_temp = [values_list_mensual[j]/31] * 31
            else:
                valores_diarios_temp = [values_list_mensual[j]/30] * 30
            if (j == 0):
                values_list_diario = valores_diarios_temp
            else:
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_q_max_values_DIARIO + nombre_conduccion3
        dic_PARAMS_CONDUCCIONES3_q_max_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[
                               nombre_conduccion3])
        if (i == 0):
            df_PARAMS_CONDUCCIONES3_q_max_diario = df_temp
        else:
            df_PARAMS_CONDUCCIONES3_q_max_diario = pd.concat([df_PARAMS_CONDUCCIONES3_q_max_diario.reset_index(drop=True),
                                                              df_temp.reset_index(drop=True)], axis=1)

    # (8) Parámetros para Retornos <---> Input + Output

    # Parámetros para retornos (mensual)
    # Crear diccionario de parámetros de demanda mensual para retornos
    dic_PARAMS_RETORNOS_demanda_mensual = {}

    # Parámetros para retornos (diario)
    # Crear diccionario de parámetros de demanda diaria para retornos
    dic_PARAMS_RETORNOS_demanda_diario = {}

    # Run for loop
    for i in range(df_pdf_retornos.shape[0]):
        # Determinamos el nombre del retorno
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_retorno = df_pdf_retornos[CFSDR_col_nombre].iloc[i].replace(
            '"', '')

        # A continuación, comprobar si es un destino de alguna toma de demanda
        # Inicializar values_list_mensual con (N_MESES_YEAR_ESTANDAR = 12) valores de 0.0
        values_list_mensual = [0.0] * N_MESES_YEAR_ESTANDAR
        # Inicializar values_list_diario con (N_DIAS_YEAR_ESTANDAR = 366) valores de 0.0
        values_list_diario = [0.0] * N_DIAS_YEAR_ESTANDAR
        for j in range(CFSDD_max_n_tomas):
            df_toma = df_pdf_demandas[df_pdf_demandas[CFSDD_col_n_elemento_retorno +
                                                      '_' + str(j+1)] == df_pdf_retornos[CFSDR_col_n_retorno].iloc[i]]
            if (df_toma.shape[0] > 0):  # Se ha encontrado la toma

                # Actualizamos values_list_mensual y values_list_diario.
                # Primero, determinamos el nombre de la demanda correspondiente.
                # NOTA: al nombre del elemento, le quitamos las comillas.
                demanda = df_toma[CFSDD_col_nombre].values[0].replace('"', '')

                # Valores mensuales
                values_list_mensual = list(map(add, values_list_mensual,
                                               df_PARAMS_DEMANDAS_mensual[demanda].values * df_toma[CFSDD_col_coef_retorno + '_' + str(j+1)].values[0]))

                # Valores diarios
                values_list_diario = list(map(add, values_list_diario,
                                              df_PARAMS_DEMANDAS_diario[demanda].values * df_toma[CFSDD_col_coef_retorno + '_' + str(j+1)].values[0]))

        # Ahora, crear los parámetros (MENSUAL)
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_demanda_retorno_values_MENSUAL + nombre_retorno
        dic_PARAMS_RETORNOS_demanda_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        df_temp = pd.DataFrame(values_list_mensual, columns=[nombre_retorno])
        if (i == 0):
            df_PARAMS_RETORNOS_demanda_mensual = df_temp
        else:
            df_PARAMS_RETORNOS_demanda_mensual = pd.concat([df_PARAMS_RETORNOS_demanda_mensual.reset_index(drop=True),
                                                            df_temp.reset_index(drop=True)], axis=1)

        # Ahora, crear los parámetros (DIARIO)
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_demanda_retorno_values_DIARIO + nombre_retorno
        dic_PARAMS_RETORNOS_demanda_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        df_temp = pd.DataFrame(values_list_diario, columns=[nombre_retorno])
        if (i == 0):
            df_PARAMS_RETORNOS_demanda_diario = df_temp
        else:
            df_PARAMS_RETORNOS_demanda_diario = pd.concat([df_PARAMS_RETORNOS_demanda_diario.reset_index(drop=True),
                                                           df_temp.reset_index(drop=True)], axis=1)

    # (9) Parámetros para acuíferos (mensual)
    # Crear diccionario de parámetros de volumen de recarga mensual para acuiferos
    dic_PARAMS_ACUIFEROS_recarga_mensual = {}

    # Parámetros para acuíferos (diario)
    # Crear diccionario de parámetros de volumen de recarga diario para acuiferos
    dic_PARAMS_ACUIFEROS_recarga_diario = {}

    # Run for loop
    for i in range(df_pdf_acuiferos.shape[0]):
        # Determinamos el nombre del acuifero
        # NOTA: al nombre del elemento, le quitamos las comillas.
        nombre_acuifero = df_pdf_acuiferos[CFSDAC_col_nombre].iloc[i].replace(
            '"', '')

        # (1.1) Empezamos con los parámetros de volumen de recarga mensual para acuiferos:
        values_str_mensual = df_pdf_acuiferos[CFSDAC_col_recarga_mensual_12_vals].iloc[i]
        # Hay casos en los que no se define la recarga, por tanto,
        if (values_str_mensual != values_str_mensual):
            # hay que considerarlo (NOTA: esta forma de hacer el if() es una forma
            # de saber si un string es NaN.
            # Creamos un una lista de [0.0] 12 veces
            values_list_mensual = [0.0] * 12
        else:
            values_list_mensual = [float(j)
                                   for j in values_str_mensual.split()]

        # Seguimos
        parametro = MonthlyProfileParameter(model, values_list_mensual)
        parametro.name = PARAM_NOMBRE_recarga_acuifero_values_MENSUAL + nombre_acuifero
        dic_PARAMS_ACUIFEROS_recarga_mensual[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_mensual, columns=[nombre_acuifero])
        if (i == 0):
            df_PARAMS_ACUIFEROS_recarga_mensual = df_temp
        else:
            df_PARAMS_ACUIFEROS_recarga_mensual = pd.concat([df_PARAMS_ACUIFEROS_recarga_mensual.reset_index(drop=True),
                                                             df_temp.reset_index(drop=True)], axis=1)

        # (1.2) Lo replicamos para el paso diario
        # NOTA importante sobre "DailyProfileParameter":
        # "An annual profile consisting of daily values.
        # This parameter provides a repeating annual profile with a daily resolution.
        # A total of 366 values must be provided. These values are coerced to a numpy.array internally."
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
                values_list_diario = values_list_diario + valores_diarios_temp

        # Ahora, crear el parámetro
        parametro = DailyProfileParameter(model, values_list_diario)
        parametro.name = PARAM_NOMBRE_recarga_acuifero_values_DIARIO + nombre_acuifero
        dic_PARAMS_ACUIFEROS_recarga_diario[parametro.name] = parametro

        # Adicionalmente, guardamos los parámetros en un df que necesitaremos en la parte guardado de los resultados
        # NOTA: al nombre del elemento, le quitamos las comillas.
        df_temp = pd.DataFrame(values_list_diario, columns=[nombre_acuifero])
        if (i == 0):
            df_PARAMS_ACUIFEROS_recarga_diario = df_temp
        else:
            df_PARAMS_ACUIFEROS_recarga_diario = pd.concat([df_PARAMS_ACUIFEROS_recarga_diario.reset_index(drop=True),
                                                            df_temp.reset_index(drop=True)], axis=1)

    # 2.2 Create nodes and edges. We start with nodes, in the following order and mapping
    '''
    (0) Nudo <---> Link
    NOTA: el nodo cuyo nombre es "Nudo Final", debe ser creado como Output.
          Este nodo se guardará en la variable específica g_nudo_final.
    (1) Embalse <---> Storage
    (2) Aportacion <---> Input
    (3) Demanda <---> Output
    (4) Toma <---> MultiSplitLink
    (5) Conduccion1 <---> LossLink
    (6) Conduccion3 <---> LossLink
    (7) Bombeo <---> Link
    (8) Retorno <---> Input + Output
    (9) Acuifero <---> Input [+ Storage]
    *(10) RETORNO_GLOBAL <---> Output: Se trata de un elemento que en realidad no existe pero que por el momento
                                       lo creamos hasta definir el nodo de retorno que hay que declarar / definir
                                       para la salida 'split_retorno' de las tomas; por el momento, conectaremos
                                       todas las salidas 'split_retorno' de todas las tomas a este elemento.
    '''

    # (0) Nudo <---> Link
    # First, determine key columns
    g_col_tipo_elemento_nombre = df_config_tpatdff[CFSIFtdf_col_tipo_elemento_nombre].iloc[0]
    g_col_elemento_id = df_config_tpatdff[CFSIFtdf_col_elemento_id].iloc[0]
    g_col_elemento_nombre = df_config_tpatdff[CFSIFtdf_col_elemento_nombre].iloc[0]
    g_col_elemento_nodo_origen = df_config_tpatdff[CFSIFtdf_col_elemento_nodo_origen].iloc[0]
    g_col_elemento_nodo_destino_demanda = df_config_tpatdff[
        CFSIFtdf_col_elemento_nodo_destino_demanda].iloc[0]
    g_col_elemento_nodo_destino_retorno = df_config_tpatdff[
        CFSIFtdf_col_elemento_nodo_destino_retorno].iloc[0]
    g_nombre_nodo_final = df_config_tpatdff[CFSIFtdf_col_nombre_nodo_final].iloc[0]
    g_col_demanda_tipo = df_config_tpatdff[CFSIFtdf_col_tipo_demanda].iloc[0]
    g_col_demanda_tipo_nombre = df_config_tpatdff[CFSIFtdf_col_tipo_demanda_nombre].iloc[0]
    g_col_demanda_mi_id = df_config_tpatdff[CFSIFtdf_col_demanda_mi_id].iloc[0]

    # In case random values are assigned to nodes as initialistion values, the random number generator must be initialised.
    random.seed()

    # (0) Nudo <---> Link
    # Now, create the corresponding elements
    # Crear dataframe de nudos
    df_nudos = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Nudo']
    dic_nudos = {}  # Crear diccionario de nudos

    # Run for loop
    for i in range(df_nudos.shape[0]):
        # NOTA: el nodo cuyo nombre es g_nombre_nodo_final, debe ser creado como Output.
        #       Este nodo se guardará en la variable específica g_nudo_final.
        if (df_nudos[g_col_elemento_nombre].iloc[i] == g_nombre_nodo_final):
            # Crear elemento Nudo para g_nudo_final como Output
            nudo = Output(model, name=str(df_nudos[g_col_elemento_id].iloc[i]),
                          comment=df_nudos[g_col_elemento_nombre].iloc[i])  # In .comment we store node's name (ID in .name)

            # Guardamos este nudo en una variables específica llamada g_nudo_final
            g_nudo_final = nudo
        else:
            # Crear elemento Nudo estándar (Link)
            nudo = Link(model, name=str(df_nudos[g_col_elemento_id].iloc[i]),
                        comment=df_nudos[g_col_elemento_nombre].iloc[i])  # In .comment we store node's name (ID in .name)

        # Actualizar dicccionario de nudos
        dic_nudos[nudo.name] = nudo

    # (1) Embalse <---> Storage
    # Crear dataframe de embalses
    df_embalses = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Embalse']
    dic_embalses = {}  # Crear diccionario de embalses

    # Run for loop
    for i in range(df_embalses.shape[0]):
        # Crear elemento Embalse (Storage)
        # In .comment we store node's name (ID in .name)
        embalse = Storage(model, name=str(
            df_embalses[g_col_elemento_id].iloc[i]), comment=df_embalses[g_col_elemento_nombre].iloc[i])

        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            embalse = InicializarEmbalse_ARTIFICIAL(embalse)
        else:
            embalse = InicializarEmbalse_con_datos_SIMGES(embalse, df_pdf_embalses, p_simulation_step,
                                                          dic_PARAMS_EMBALSES_vol_min_mensual, dic_PARAMS_EMBALSES_vol_max_mensual,
                                                          dic_PARAMS_EMBALSES_vol_min_diario, dic_PARAMS_EMBALSES_vol_max_diario)

        # Actualizar dicccionario de embalses
        dic_embalses[embalse.name] = embalse

    # (2) Aportacion <---> Input
    # Crear dataframe de aportaciones
    df_aportaciones = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre]
                                 == 'Aportacion']
    dic_aportaciones = {}  # Crear diccionario de aportaciones

    # Run for loop
    for i in range(df_aportaciones.shape[0]):
        # Crear elemento Aportacion (Input)
        # In .comment we store node's name (ID in .name)
        aportacion = Input(model, name=str(
            df_aportaciones[g_col_elemento_id].iloc[i]), comment=df_aportaciones[g_col_elemento_nombre].iloc[i])

        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            aportacion = InicializarAportacion_ARTIFICIAL(aportacion)
        else:
            aportacion = InicializarAportacion_con_datos_SIMGES(aportacion, df_pdf_aportaciones, p_simulation_step,
                                                                dic_PARAMS_APORTACIONES_mensual, dic_PARAMS_APORTACIONES_diario)

        # Actualizar dicccionario de aportaciones
        dic_aportaciones[aportacion.name] = aportacion

    # (3) Demanda <---> Output
    # Crear dataframe de demandas
    df_demandas = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Demanda']
    dic_demandas = {}  # Crear diccionario de demandas

    # Run for loop
    for i in range(df_demandas.shape[0]):
        # Crear elemento Demanda (Output)
        # In .comment we store node's name (ID in .name)
        demanda = Output(model, name=str(
            df_demandas[g_col_elemento_id].iloc[i]), comment=df_demandas[g_col_elemento_nombre].iloc[i])
        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            demanda = InicializarDemanda_ARTIFICIAL(demanda)
        else:
            demanda = InicializarDemanda_con_datos_SIMGES(demanda, df_pdf_demandas, p_simulation_step,
                                                          dic_PARAMS_DEMANDAS_mensual, dic_PARAMS_DEMANDAS_diario)

        # Actualizar deccionario de demandas
        dic_demandas[demanda.name] = demanda

    # (4) Toma <---> MultiSplitLink
    # Crear dataframe de tomas
    df_tomas = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Toma']
    dic_tomas = {}  # Crear diccionario de tomas

    # Run for loop
    for i in range(df_tomas.shape[0]):
        # Crear elemento Toma (MultiSplitLink)
        # Elemento MultiSplitLink. NOTE: 2 outputs are considered: "split_demanda" and "split_retorno".
        toma = MultiSplitLink(model, name=str(df_tomas[g_col_elemento_id].iloc[i]), comment=df_tomas[g_col_elemento_nombre].iloc[i],
                              nsteps=1, extra_slots=1, slot_names=["split_demanda", "split_retorno"])
        # In .comment we store node's name (ID in .name)
        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            toma = InicializarToma_ARTIFICIAL(toma)
        else:
            toma = InicializarToma_con_datos_SIMGES(
                toma, df_pdf_demandas, p_simulation_step)

        # Actualizar deccionario de tomas
        dic_tomas[toma.name] = toma

    # (5) Conduccion1 <---> LossLink. NOTE: for every LossLink element, 2 edges are created.
    # Crear dataframe de conducciones1
    df_conducciones1 = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre]
                                  == 'Conduccion1']
    dic_conducciones1 = {}  # Crear diccionario de conducciones1

    # Run for loop
    for i in range(df_conducciones1.shape[0]):
        # Crear elemento Conducciones1 (LossLink)
        # In .comment we store node's name (ID in .name)
        conduccion1 = LossLink(model, name=str(
            df_conducciones1[g_col_elemento_id].iloc[i]), comment=df_conducciones1[g_col_elemento_nombre].iloc[i])
        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            conduccion1 = InicializarConduccion1_ARTIFICIAL(conduccion1)
        else:
            conduccion1 = InicializarConduccion1_con_datos_SIMGES(conduccion1, df_pdf_conducciones1, p_simulation_step,
                                                                  dic_PARAMS_CONDUCCIONES1_q_min_mensual, dic_PARAMS_CONDUCCIONES1_q_max_mensual,
                                                                  dic_PARAMS_CONDUCCIONES1_q_min_diario, dic_PARAMS_CONDUCCIONES1_q_max_diario)

        # Actualizar deccionario de conducciones1
        dic_conducciones1[conduccion1.name] = conduccion1

    # (6) Conduccion3 <---> LossLink. NOTE: for every LossLink element, 2 edges are created.
    # Crear dataframe de conducciones3
    df_conducciones3 = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre]
                                  == 'Conduccion3']
    dic_conducciones3 = {}  # Crear diccionario de conducciones3

    # Run for loop
    for i in range(df_conducciones3.shape[0]):
        # Crear elemento Conducciones3 (LossLink)
        # In .comment we store node's name (ID in .name)
        conduccion3 = LossLink(model, name=str(
            df_conducciones3[g_col_elemento_id].iloc[i]), comment=df_conducciones3[g_col_elemento_nombre].iloc[i])
        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            conduccion3 = InicializarConduccion3_ARTIFICIAL(conduccion3)
        else:
            conduccion3 = InicializarConduccion3_con_datos_SIMGES(conduccion3, df_pdf_conducciones3, p_simulation_step,
                                                                  dic_PARAMS_CONDUCCIONES3_q_min_mensual, dic_PARAMS_CONDUCCIONES3_q_max_mensual,
                                                                  dic_PARAMS_CONDUCCIONES3_q_min_diario, dic_PARAMS_CONDUCCIONES3_q_max_diario)

        # Actualizar deccionario de conducciones3
        dic_conducciones3[conduccion3.name] = conduccion3

    # (7) Bombeo <---> Link
    # Crear dataframe de bombeos
    df_bombeos = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Bombeo']
    dic_bombeos = {}  # Crear diccionario de bombeos

    # Run for loop
    for i in range(df_bombeos.shape[0]):
        # Crear elemento Bombeo (Link)
        # In .comment we store node's name (ID in .name)
        bombeo = Link(model, name=str(
            df_bombeos[g_col_elemento_id].iloc[i]), comment=df_bombeos[g_col_elemento_nombre].iloc[i])

        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            bombeo = InicializarBombeo_ARTIFICIAL(bombeo)
        else:
            bombeo = InicializarBombeo_con_datos_SIMGES(
                bombeo, df_pdf_bombeos, p_simulation_step)

        # Actualizar deccionario de bombeos
        dic_bombeos[bombeo.name] = bombeo

    # (8) Retorno <---> Input + Output
    # Creamos un elemento de tipo OUTPUT para acumular cada uno de los retornos, para compararlos al final de una simulación
    # con los del INPUT, de manera que podremos evaluar si estamos utilizando o no correctamente las entradas de retorno.

    # Crear dataframe de retornos
    df_retornos = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Retorno']

    # Por el momento no creamos un diccionario de retornos, porque lo que haremos será conectar la salida de retorno
    # de la toma correspondiente al nodo que alimenta el retorno.

    dic_retornos_input = {}  # Crear diccionario de retornos de entrada
    dic_retornos_output = {}  # Crear diccionario de retornos de almacenamiento

    # Run for loop
    for i in range(df_retornos.shape[0]):
        # Crear elemento Retorno (Input)
        # In .comment we store node's name (ID in .name)
        retorno_input = Input(model, name=str(
            df_retornos[g_col_elemento_id].iloc[i]) + '_input', comment=df_retornos[g_col_elemento_nombre].iloc[i])

        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            retorno_input = InicializarRetorno_Input_ARTIFICIAL(retorno_input)
        else:
            retorno_input = InicializarRetorno_Input_con_datos_SIMGES(
                retorno_input)

        # Actualizar deccionario de retornos de entrada
        dic_retornos_input[retorno_input.name] = retorno_input

        # Crear elemento Retorno (Output)
        # Primero, verificar si en el archivo de datos físicos se indica que este retorno es el destino de alguna demanda
        bln_Y_N = VerificarSiNodoEsRetornoDeNodoDeDemandaEnArchivoDatosFisicos(df_retornos[g_col_elemento_nombre].iloc[i], df_pdf_retornos,
                                                                               df_pdf_demandas)
        if (bln_Y_N == True):
            # Crear el nodo de retorno (salida)
            # In .comment we store node's name (ID in .name)
            retorno_output = Output(model, name=str(
                df_retornos[g_col_elemento_id].iloc[i]) + '_output', comment=df_retornos[g_col_elemento_nombre].iloc[i])

            # Etablecemos los mismos valores de inicialización que para el retorno_input
            if (blnInicializar_con_valores_artificiales_y_n == True):
                IgualarValoresInicializacionRetornos_ARTIFICIAL(
                    retorno_output, dic_retornos_input)
            else:
                retorno_output = InicializarRetorno_Output_con_datos_SIMGES(retorno_output, df_pdf_retornos, p_simulation_step,
                                                                            dic_PARAMS_RETORNOS_demanda_mensual, dic_PARAMS_RETORNOS_demanda_diario)
                IgualarValoresInicializacionRetornos_con_datos_SIMGES(
                    retorno_output, dic_retornos_input)

            # Actualizar deccionario de retornos de almacenamiento
            dic_retornos_output[retorno_output.name] = retorno_output

    # (9) Acuifero <---> Input + [Storage]
    # Crear dataframe de acuíferos
    df_acuiferos = df_tpatdff[df_tpatdff[g_col_tipo_elemento_nombre] == 'Acuifero']
    dic_acuiferos = {}  # Crear diccionario de acuíferos

    # Run for loop
    for i in range(df_acuiferos.shape[0]):
        # Crear elemento Acuifero (Input)
        # In .comment we store node's name (ID in .name)
        acuifero = Input(model, name=str(
            df_acuiferos[g_col_elemento_id].iloc[i]), comment=df_acuiferos[g_col_elemento_nombre].iloc[i])

        # LLamada a función de inicialización
        if (blnInicializar_con_valores_artificiales_y_n == True):
            acuifero = InicializarAcuifero_ARTIFICIAL(acuifero)
        else:
            acuifero = InicializarAcuifero_con_datos_SIMGES(acuifero, df_pdf_acuiferos, p_simulation_step,
                                                            dic_PARAMS_ACUIFEROS_recarga_mensual, dic_PARAMS_ACUIFEROS_recarga_diario)

        # Actualizar deccionario de acuíferos
        dic_acuiferos[acuifero.name] = acuifero

    # ***(10) RETORNO_GLOBAL <---> Output: Se trata de un elemento que en realidad no existe pero que por el momento
    # lo creamos hasta definir el nodo de retorno que hay que declarar / definir
    # para la salida 'split_retorno' de las tomas; por el momento, conectaremos
    # todas las salidas 'split_retorno' de todas las tomas a este elemento.

    g_retorno_global = Output(model, name='g_retorno_global',
                              comment='g_retorno_global')  # In .comment we store node's name (ID in .name)

    # 2.3 We continue with edges, in the following order and mapping
    '''
    (2) Aportacion <---> Input
    
        (a) Hay que crear un edge entre la propia aportación y el elemento que marca el campo NudoDestino.
            NOTA: El valor de NudoOrigen coincide con el valor de 'gfCodSig' de la propia aportación
    
    (4) Toma <---> MultiSplitLink
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la parte MultiSplitLink de la propia toma.
        (b) Hay que crear un edge entre el split 'split_demanda' de la parte MultiSplitLink de la propia toma
            y el elemento que marca el campo NudoDestino.
        (c) Hay que crear un edge entre el split 'split_retorno' de la parte MultiSplitLink de la propia toma
            y [**INICIALMENTE**] el elemento artificial global de retorno que hemos llamado 'g_retorno_global'.
    
    (5) Conduccion1 <---> LossLink
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la propia Conduccion1.
        (b) Hay que crear un edge entre la propia Conduccion1 y el elemento que marca el campo NudoDestino.
        
    (6) Conduccion3 <---> LossLink
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la propia Conduccion1.
        (b) Hay que crear un edge entre la propia Conduccion1 y el elemento que marca el campo NudoDestino.
        
    (7) Bombeo <---> Link
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y el propio bombeo.
        (b) Hay que crear un edge entre el propio bombeo y el elemento que marca el campo NudoDestino.
    
    (8) Retorno <---> Input + Output
    
        ***(a) Por el momento nada: cuando se haya definido en el archivo "OUT_tpl.tpa_to_dataframe_EXTENDED.xlsx"
               el destino del split2 ("split_retorno") en tomas, ya se habrá creado un edge entre aquel split2 ("split_retorno")
               y este retorno.
        (b) Hay que crear un edge entre el propio retorno y el elemento que marca el campo NudoDestino.
    
    '''

    # NOTA: OJOOOOOOOOOOOOOOOOOOOOOOOOOOOOO !!!
    #
    #       Los nodos de tipo Storage, MultiSplitLink y LossLink tienen sus atributos
    #       nodo.model.graph.predecessors(nodo) y nodo.model.graph.successors(nodo) a 0 !!!
    #
    #       Esto se debe a que los nodos, en general, incluyen múltiples elementos internos y, por ello,
    #       en el caso de los nodos de tipo Storage, MultiSplitLink y LossLink, las conexiones con ellos se realizan
    #       a través de elementos internos de los mismos.
    #
    #       Por tanto, a la hora de hacer la búsqueda de nodos sucesores y predecesores de este tipo de nodos,
    #       hay que seguir las siguientes reglas:
    #
    #       (1) nodos de tipo Storage:
    #           + La lista de nodos predecesores se encuentra en su propiedad .outputs[0]. Ejemplo:
    #
    #             storage_predecessors = list(storage.outputs[0].model.graph.predecessors(storage.outputs[0]))
    #
    #           + La lista de nodos sucesores se encuentra en su propiedad .inputs[0]. Ejemplo:
    #
    #             storage_successors = list(storage.inputs[0].model.graph.successors(storage.inputs[0]))
    #
    #       (2) nodos de tipo MultiSplitLink:
    #           + La lista de nodos predecesores se encuentra en su propiedad .output. Ejemplo:
    #
    #             multi_split_link_predecessors = list(multi_split_link.output.model.graph.predecessors(multi_split_link.output))
    #
    #           + La lista de nodos sucesores se encuentra en sus propiedades .inputs y ._extra_inputs[n],
    #             donde n toma valores entra 0 y n_extra_slots - 1. Como en nuestro siempre caso n_extra_slots = 1, podemos decir
    #             que La lista de nodos sucesores se encuentra en sus propiedades .inputs y ._extra_inputs[0]. Ejemplo:
    #
    #             multi_split_link_successors_1 = list(multi_split_link.input.model.graph.successors(multi_split_link.input))
    #             multi_split_link_successors_2 = list(multi_split_link._extra_inputs[0].model.graph.successors(multi_split_link._extra_inputs[0]))
    #
    #       (3) nodos de tipo LossLink:
    #           + La lista de nodos predecesores se encuentra en su propiedad .gross. Ejemplo:
    #
    #             loss_link_predecessors = list(loss_link.gross.model.graph.predecessors(loss_link.gross))
    #
    #           + La lista de nodos sucesores se encuentra en su propiedad .net. Ejemplo:
    #
    #             loss_link_successors = list(loss_link.net.model.graph.successors(loss_link.net))
    #
    #       (4) resto de tipo de nodos aquí utilizados (Node, Input, Output, Link) :
    #           + La lista de nodos predecesores se encuentra desde el propio nodo. Ejemplo:
    #
    #             predecessors_nodo = list(nodo.gross.model.graph.predecessors(nodo))
    #
    #           + La lista de nodos sucesores se encuentra desde el propio nodo. Ejemplo:
    #
    #             successors_nodo = list(nodo.gross.model.graph.successors(nodo))
    #
    # Por otro lado, hay que tener en cuenta que como los elementos de este tipo de nodos a los que se conectan otros
    # nodos son "hijos" de ellos, cuando un nodo "nodo_1" esté conectado a cualquiera de este tipo de nodos, a la hora
    # determinar los nodos predecesores o sucesores de "nodo_1", habrá que ir a la propiedad ".parent" de los elementos
    # resultantes. Por ejemplo:
    #
    # Supongamos que un nodo de tipo Supply está conectado a un nodo de tipo LossLink. Para acceder al nodo de tipo LossLink
    # al que está conectado el nodo de tipo Supply, hay que hacer lo siguiente:
    #
    #            supply_successors = list(supply.model.graph.successors(supply))
    #            succesor_node = supply_successors[0].parent
    #
    # Por tanto, lo que haremos a la hora de buscar los nodos predecesores y sucesores es siempre apuntar primero a la
    # propiedad ".parent" del correspondiente predecesor y sucesor, y si el valor es None, entonces significa que podemos
    # apuntar al propio predecesor o sucesor.

    # edges for (2) Aportacion
    '''
    (2) Aportacion <---> Input
    
        (a) Hay que crear un edge entre la propia aportación y el elemento que marca el campo NudoDestino.
            NOTA: El valor de NudoOrigen coincide con el valor de 'gfCodSig' de la propia aportación
    '''
    # Run for loop
    for aportacion in dic_aportaciones:
        # Get destination node ID (destination node 'gfCodSig' value)
        intNudoDestino = int(df_aportaciones[df_aportaciones[g_col_elemento_id] == int(
            aportacion)][g_col_elemento_nodo_destino_demanda].values[0])

        # Now, get the destination node in the model
        NudoDestino = model.nodes.__getitem__(str(intNudoDestino))

        # Now, create the connection from current node aportacion to NudoDestino
        dic_aportaciones[aportacion].connect(NudoDestino)

    # edges for (4) Toma <---> MultiSplitLink
    '''
    (4) Toma <---> MultiSplitLink
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la parte MultiSplitLink de la propia toma.
        (b) Hay que crear un edge entre el split 'split_demanda' de la parte MultiSplitLink de la propia toma
            y el elemento que marca el campo NudoDestino.
        (c) Creamos un edge entre el split 'split_retorno' de la parte MultiSplitLink de la propia toma
            y el elemento output de retorno creado.
    '''

    # IMPORTANTE: Hay que utilizar los datos de las pestañas en la que se encuentra la información que nos interesa
    # sobre la relación entre las tomas y los retornos.
    # Run for loop
    for i in range(df_tomas.shape[0]):
        # (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la parte MultiSplitLink de la propia toma.

        # toma
        toma = dic_tomas[str(df_tomas[g_col_elemento_id].iloc[i])]

        # Get origin node ID (origin node 'gfCodSig' value)
        intNudoOrigen = int(df_tomas.iloc[i][g_col_elemento_nodo_origen])

        # Now, get the destination node in the model
        NudoOrigen = model.nodes.__getitem__(str(intNudoOrigen))

        # Edge entre NudoOrigen y toma
        NudoOrigen.connect(toma)

        # (b) Hay que crear un edge entre el split 'split_demanda' de la parte MultiSplitLink de la propia toma
        #     y el elemento que marca el campo NudoDestino.

        # Get destination node ID (destination node 'gfCodSig' value)
        intNudoDestino = int(
            df_tomas.iloc[i][g_col_elemento_nodo_destino_demanda])

        # Now, get the destination node in the model
        NudoDestino = model.nodes.__getitem__(str(intNudoDestino))

        # Edge entre "split_demanda" de toma y NudoDestino
        toma.connect(NudoDestino, "split_demanda", None)

        # (c) Creamos un edge entre el split 'split_retorno' de la parte MultiSplitLink de la propia toma
        #     y el elemento output de retorno creado.
        for j in range(CFSDD_max_n_tomas):
            df_toma = df_pdf_demandas[df_pdf_demandas[CFSDD_col_nombre_toma +
                                                      '_' + str(j+1)] == '"' + toma.comment + '"']
            if (df_toma.shape[0] > 0):  # Se ha encontrado la toma
                # Ahora, identificar el nombre de retorno en df_pdf_retornos
                # Si el número de identificador es 0, normalmente significa que el coeficiente de retorno es 0, pero,
                # he visto que hay un caso en el que el coeficiente es mayor que 0. Por tanto, lo que haremos es conectar
                # las tomas que tengan como identificador de retorno el número 0, al retorno global g_retorno_global.
                if (int(df_toma[CFSDD_col_n_elemento_retorno + '_' + str(j+1)].values[0]) == 0):
                    toma.connect(g_retorno_global, "split_retorno", None)
                else:
                    # Obtener el nombre del elemento de retorno
                    df_retorno = df_pdf_retornos[df_pdf_retornos[CFSDR_col_n_retorno] == int(
                        df_toma[CFSDD_col_n_elemento_retorno + '_' + str(j+1)].values[0])]
                    nombre_nudo_retorno = df_retorno[CFSDR_col_nombre].values[0]

                    # Caso 1, cuando la conexión de feedback loop desde el split de retorno se hace al mismo elemento de retorno,
                    # a su parte output

                    # Obtener el identificador del elemento de retorno.
                    # IMPORTANTE: el string del nombre del nudo destino tiene doble comilla " al inicio y al final, por lo que
                    # hay que quitárselas.
                    intNudoDestino = int(
                        df_retornos[df_retornos[g_col_elemento_nombre] == nombre_nudo_retorno[1:-1]][g_col_elemento_id].values[0])

                    # Obtener el nodo de retorno (output)
                    NudoDestino = model.nodes.__getitem__(
                        str(intNudoDestino) + '_output')

                    # Now, create the connection from current node aportacion to NudoDestino
                    toma.connect(NudoDestino, "split_retorno", None)

                break  # Finish outer for loop

    # edges for (5) Conduccion1 <---> LossLink

    '''
    (5) Conduccion1 <---> LossLink
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la propia Conduccion1.
        (b) Hay que crear un edge entre la propia Conduccion1 y el elemento que marca el campo NudoDestino.
    '''
    # Run for loop
    for conduccion1 in dic_conducciones1:
        # (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la propia Conduccion1.

        # Get origin node ID (origin node 'gfCodSig' value)
        intNudoOrigen = int(df_conducciones1[df_conducciones1[g_col_elemento_id] == int(
            conduccion1)][g_col_elemento_nodo_origen].values[0])

        # Now, get the destination node in the model
        NudoOrigen = model.nodes.__getitem__(str(intNudoOrigen))

        # Now, create the connection from NudoOrigen to current node conduccion1
        NudoOrigen.connect(dic_conducciones1[conduccion1])

        # (b) Hay que crear un edge entre la propia Conduccion1 y el elemento que marca el campo NudoDestino.

        # Get destination node ID (destination node 'gfCodSig' value)
        intNudoDestino = int(df_conducciones1[df_conducciones1[g_col_elemento_id] == int(
            conduccion1)][g_col_elemento_nodo_destino_demanda].values[0])

        # Now, get the destination node in the model
        NudoDestino = model.nodes.__getitem__(str(intNudoDestino))

        # Now, create the connection from current node aportacion to NudoDestino
        dic_conducciones1[conduccion1].connect(NudoDestino)

    # edges for (6) Conduccion3 <---> LossLink

    '''
    (6) Conduccion3 <---> LossLink
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la propia Conduccion3.
        (b) Hay que crear un edge entre la propia Conduccion3 y el elemento que marca el campo NudoDestino.
    '''
    # Run for loop
    for conduccion3 in dic_conducciones3:
        # (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y la propia Conduccion3.

        # Get origin node ID (origin node 'gfCodSig' value)
        intNudoOrigen = int(df_conducciones3[df_conducciones3[g_col_elemento_id] == int(
            conduccion3)][g_col_elemento_nodo_origen].values[0])

        # Now, get the destination node in the model
        NudoOrigen = model.nodes.__getitem__(str(intNudoOrigen))

        # Now, create the connection from NudoOrigen to current node conduccion3
        NudoOrigen.connect(dic_conducciones3[conduccion3])

        # (b) Hay que crear un edge entre la propia Conduccion3 y el elemento que marca el campo NudoDestino.

        # Get destination node ID (destination node 'gfCodSig' value)
        intNudoDestino = int(df_conducciones3[df_conducciones3[g_col_elemento_id] == int(
            conduccion3)][g_col_elemento_nodo_destino_demanda].values[0])

        # Now, get the destination node in the model
        NudoDestino = model.nodes.__getitem__(str(intNudoDestino))

        # Now, create the connection from current node aportacion to NudoDestino
        dic_conducciones3[conduccion3].connect(NudoDestino)

    # edges for (7) Bombeo <---> Link

    '''
    (7) Bombeo <---> Link
    
        (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y el propio bombeo.
        (b) Hay que crear un edge entre el propio bombeo y el elemento que marca el campo NudoDestino.
    '''
    # Run for loop
    for bombeo in dic_bombeos:
        # (a) Hay que crear un edge entre el elemento que marca el campo NudoOrigen y el propia bombeo.

        # Get origin node ID (origin node 'gfCodSig' value)
        intNudoOrigen = int(df_bombeos[df_bombeos[g_col_elemento_id] == int(
            bombeo)][g_col_elemento_nodo_origen].values[0])

        # Now, get the destination node in the model
        NudoOrigen = model.nodes.__getitem__(str(intNudoOrigen))

        # Now, create the connection from NudoOrigen to current node bombeo
        NudoOrigen.connect(dic_bombeos[bombeo])

        # (b) Hay que crear un edge entre el propia bombeo y el elemento que marca el campo NudoDestino.

        # Get destination node ID (destination node 'gfCodSig' value)
        intNudoDestino = int(df_bombeos[df_bombeos[g_col_elemento_id] == int(
            bombeo)][g_col_elemento_nodo_destino_demanda].values[0])

        # Now, get the destination node in the model
        NudoDestino = model.nodes.__getitem__(str(intNudoDestino))

        # Now, create the connection from current node aportacion to NudoDestino
        dic_bombeos[bombeo].connect(NudoDestino)

    # edges for (8) Retorno <---> Input + Output

    '''
    (8) Retorno <---> Input + Output
    
        ***(a) Por el momento nada: cuando se haya definido en el archivo "OUT_tpl.tpa_to_dataframe_EXTENDED.xlsx"
               el destino del split2 ("split_retorno") en tomas, ya se habrá creado un edge entre aquel split2 ("split_retorno")
               y este retorno.
        (b) Hay que crear un edge entre el propio retorno y el elemento que marca el campo NudoDestino.
    '''
    # Run for loop
    for retorno in dic_retornos_input:
        # ***(a) Por el momento nada: cuando se haya definido en el archivo "OUT_tpl.tpa_to_dataframe_EXTENDED.xlsx"
        #        el destino del split2 ("split_retorno") en tomas, ya se habrá creado un edge entre aquel split2 ("split_retorno")
        #        y este retorno.

        # (b) Hay que crear un edge entre el propia retorno y el elemento que marca el campo NudoDestino.

        # Get destination node ID (destination node 'gfCodSig' value)
        # IMPORTANTE: recordar que al ID del retorno le hemos añadido el sufijo '_input' y que a la hora de buscar y que pot tanto
        #             a la hora de buscar el ID en df_retornos, hay que eliminar el sufijo.
        intNudoDestino = int(df_retornos[df_retornos[g_col_elemento_id] == int(
            retorno.replace('_input', ''))][g_col_elemento_nodo_destino_demanda].values[0])

        # Now, get the destination node in the model
        NudoDestino = model.nodes.__getitem__(str(intNudoDestino))

        # Now, create the connection from current node aportacion to NudoDestino
        dic_retornos_input[retorno].connect(NudoDestino)

    '''
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    '''

    # Verificamos si hay excepciones en la red que haya que tratar de manera especial.
    # Concretamente, se verifica si hay nodos que no tienen ni precedecores ni sucerores, y se guardan las excepciones,
    # es decir, los datos de dichos nodos, en un archivo definido en la pestaña CF_SHEET_EXCEPTIONS_FILE del archivo
    # de configuración CONFIG_FILE.
    # Primero, guardamos todos los nodos creados en un único diccionario
    dic_all_nodes = dic_nudos.copy()
    dic_all_nodes.update(dic_embalses)
    dic_all_nodes.update(dic_aportaciones)
    dic_all_nodes.update(dic_demandas)
    dic_all_nodes.update(dic_tomas)
    dic_all_nodes.update(dic_conducciones1)
    dic_all_nodes.update(dic_conducciones3)
    dic_all_nodes.update(dic_bombeos)
    dic_all_nodes.update(dic_retornos_input)
    dic_all_nodes.update(dic_retornos_output)
    dic_all_nodes.update(dic_acuiferos)
    dic_nodo_retorno_global = {}
    dic_nodo_retorno_global[g_retorno_global.name] = g_retorno_global
    dic_all_nodes.update(dic_nodo_retorno_global)

    # A continuación, comprobamos qué nodos no tienen ni predecesores ni sucesores en dic_all_nodes{}

    # Obtener los datos de configuración
    df_config_exceptions_file = xl_cf.parse(
        sheet_name=CF_SHEET_EXCEPTIONS_FILE, header=CFSEF_HEADER)

    # Creamos un data frame para guardar los nodos
    df_excepciones = pd.DataFrame()

    # Empezamos la vereficación
    n_exceptions = 0  # Inicialización
    for nodo in dic_all_nodes:
        lstPredecesores = GetPredecessorList(dic_all_nodes[nodo])
        lstSucesores = GetSuccessorList(dic_all_nodes[nodo])
        if ((len(lstPredecesores) + len(lstSucesores)) == 0):
            n_exceptions += 1
            if (n_exceptions == 1):
                df_excepciones[df_config_exceptions_file[CFSEF_col_id].iloc[0]] = [
                    dic_all_nodes[nodo].name]
                df_excepciones[df_config_exceptions_file[CFSEF_col_name].iloc[0]] = [
                    dic_all_nodes[nodo].comment]
                df_excepciones[df_config_exceptions_file[CFSEF_col_type].iloc[0]] = [
                    GetNodeTypeName(dic_all_nodes[nodo])]
            else:
                df_temp = pd.DataFrame()
                df_temp[df_config_exceptions_file[CFSEF_col_id].iloc[0]] = [
                    dic_all_nodes[nodo].name]
                df_temp[df_config_exceptions_file[CFSEF_col_name].iloc[0]] = [
                    dic_all_nodes[nodo].comment]
                df_temp[df_config_exceptions_file[CFSEF_col_type].iloc[0]] = [
                    GetNodeTypeName(dic_all_nodes[nodo])]
                df_excepciones = pd.concat(
                    [df_excepciones, df_temp], ignore_index=True)
    # Write exceptions to an exit Excel file
    if (n_exceptions > 0):
        with pd.ExcelWriter(df_config_exceptions_file[CFSEF_exceptions_file_path].iloc[0]) as writer:
            df_excepciones.to_excel(
                writer, sheet_name=df_config_exceptions_file[CFSEF_col_sheet_exceptions].iloc[0])

    # Ahora, toca tratar las excepciones

    '''
    ## Excepción nº 1
    
    El nodo  <Output "2361"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es una UDI ("UDI3 - CENTRO").
    + Tiene una entrada de bombeo desde el acuífero nº 24- ([ID: 2132], "VEGA ALTA"). Ver archivo "SEGU.FIS" o "datos_generales_DEMANDAS.dat"
      (este último, creado por mi).
    + Por tanto, en teoría, **SI** que habría que tenerlo en cuenta.
    
    ## Excepción nº 2
    
    El nodo  <Input "237"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("Acuifero CREVILLENTE").
    + Tiene una entrada de recarga desde "UDA 55 - ACU.CREVILLENTE".
    + Por tanto, en teoría, **SI** que habría que tenerlo en cuenta.
    
    ## Excepción nº 3
    
    El nodo  <Input "1871"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("QUIBAS").
    + No es ni salida ni entrada de ningún otro elemento.
    + Por tanto, en teoría, **NO** que habría que tenerlo en cuenta.
    
    ## Excepción nº 4
    
    El nodo  <Input "2028"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("INFILTRACION CENAJO").
    + Se define una infiltración desde el embalse del "CENAJO" a este acuífero.
    + Por tanto, en teoría, **SI** que habría que tenerlo en cuenta.
    
    ## Excepción nº 5
    
    El nodo  <Input "2046"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("ANTICLINAL DE SOCOVOS").
    + No es ni salida ni entrada de ningún otro elemento.
    + Por tanto, en teoría, **NO** que habría que tenerlo en cuenta.
    
    ## Excepción nº 6
    
    El nodo  <Input "2132"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("VEGA ALTA").
    + Es salida de "UDI3 - CENTRO".
    + Esta relación ya se tiene en cuenta en la "## Excepción nº 1", por tanto, en teoría, **NO** que habría que tenerlo en cuenta.
    
    '''

    '''
    ## Excepción nº 1
    
    El nodo  <Output "2361"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es una UDI ("UDI3 - CENTRO").
    + Tiene una entrada de bombeo desde el acuífero nº 24- ([ID: 2132], "VEGA ALTA"). Ver archivo "SEGU.FIS" o
      "datos_generales_DEMANDAS.dat" (este último, creado por mi).
    + Por tanto, en teoría, **SI** que habría que tenerlo en cuenta y crear una conexión desde el acuífero a la UDI.
    '''

    # Creamos un enlace entre el el acuífero el acuífero nº 24- ([ID: 2132], "VEGA ALTA") y la UDI "UDI3 - CENTRO".
    # Hemos comprobado que el ID de la "UDI3 - CENTRO" es [ID: 2361].
    # Identificar los elementos origen y destino:
    if (blnEliminar_nodos_aislados_y_n == True):
        #     elemento_origen = dic_acuiferos['2132']
        #     elemento_destino = dic_demandas['2361']
        elemento_origen = model.nodes.__getitem__('2132')
        elemento_destino = model.nodes.__getitem__('2361')

        # Crear la conexión
        elemento_origen.connect(elemento_destino)

    '''
    ## Excepción nº 2
    
    El nodo  <Input "237"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("Acuifero CREVILLENTE").
    + Tiene una entrada de recarga desde "UDA 55 - ACU.CREVILLENTE".
    + Por tanto, en teoría, **SI** que habría que tenerlo en cuenta.
    
    NOTA: En principio, habría que crear una conexión entre la UDA y el acuífero; PERO, como el acuífero no alimenta
          nada, por el momento, no creamos la conexión y eliminamos el nodo.
    '''

    # Por tanto, eliminamos el nodo
    if (blnEliminar_nodos_aislados_y_n == True):
        # Seleccionar el nodo
        #     nodo_a_eliminar = dic_acuiferos['237']
        nodo_a_eliminar = model.nodes.__getitem__('237')

        # Eliminar el nodo desde la estructura del modelo
        model.nodes.__delitem__(nodo_a_eliminar)

        # Eliminar el nodo desde al diccionario correspondiente
        del dic_acuiferos['237']

    '''
    ## Excepción nº 3
    
    El nodo  <Input "1871"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("QUIBAS").
    + No es ni salida ni entrada de ningún otro elemento.
    + Por tanto, en teoría, **NO** que habría que tenerlo en cuenta y eliminamos el nodo.
    '''

    # Por tanto, eliminamos el nodo
    if (blnEliminar_nodos_aislados_y_n == True):
        # Seleccionar el nodo
        #     nodo_a_eliminar = dic_acuiferos['1871']
        nodo_a_eliminar = model.nodes.__getitem__('1871')

        # Eliminar el nodo desde la estructura del modelo
        model.nodes.__delitem__(nodo_a_eliminar)

        # Eliminar el nodo desde al diccionario correspondiente
        del dic_acuiferos['1871']

    '''
    ## Excepción nº 4
    
    El nodo  <Input "2028"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("INFILTRACION CENAJO").
    + Se define una infiltración desde el embalse del "CENAJO" a este acuífero.
    + Por tanto, en teoría, **SI** que habría que tenerlo en cuenta.
    
    NOTA: En principio, habría que crear una conexión entre el embalse del "CENAJO" y el acuífero;
          PERO, como el acuífero no alimenta nada, por el momento, no creamos la conexión y eliminamos el nodo.
    '''

    # Por tanto, eliminamos el nodo
    if (blnEliminar_nodos_aislados_y_n == True):
        # Seleccionar el nodo
        #     nodo_a_eliminar = dic_acuiferos['2028']
        nodo_a_eliminar = model.nodes.__getitem__('2028')

        # Eliminar el nodo desde la estructura del modelo
        model.nodes.__delitem__(nodo_a_eliminar)

        # Eliminar el nodo desde al diccionario correspondiente
        del dic_acuiferos['2028']

    '''
    ## Excepción nº 5
    
    El nodo  <Input "2046"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("ANTICLINAL DE SOCOVOS").
    + No es ni salida ni entrada de ningún otro elemento.
    + Por tanto, en teoría, **NO** que habría que tenerlo en cuentay eliminamos el nodo.
    '''

    # Por tanto, eliminamos el nodo
    if (blnEliminar_nodos_aislados_y_n == True):
        # Seleccionar el nodo
        #     nodo_a_eliminar = dic_acuiferos['2046']
        nodo_a_eliminar = model.nodes.__getitem__('2046')

        # Eliminar el nodo desde la estructura del modelo
        model.nodes.__delitem__(nodo_a_eliminar)

        # Eliminar el nodo desde al diccionario correspondiente
        del dic_acuiferos['2046']

    '''
    ## Excepción nº 6
    
    El nodo  <Input "2132"> tiene 0 predecesores y sucesores.
    
    ### COMENTARIO
    
    + Es un acuífero ("VEGA ALTA").
    + Es salida de "UDI3 - CENTRO".
    + Esta relación ya se tiene en cuenta en la "## Excepción nº 1", por tanto, en teoría, **NO** que habría que tenerlo en cuenta
      ni hacer nada más.
    '''

    # Por tanto, NO hacemos nada

    '''
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    '''

    # IMPORTANTE: para que el agua pueda fluir por las rutas que llegan hasta su destino, principalmente las demandas
    # es necesario que la suma total de los costes de la ruta que llega hasta dicha demanda sea < 0.
    #
    # (a) Con el fin de asegurar que posibles valores positivos impidan que el agua llegue a su destino (demanda), determinamos
    # el valor máximo del coste de entre todas las posibles rutas que terminen en una demanda (g_max_coste_ruta_demandas).
    # Así, al establecer el coste (beneficio) de las demandas, su valor base deberá ser (-g_max_coste_ruta_demandas-1).
    #
    # En nuesta red, hay otras 3 posibles salidas secundarias:
    #
    # (b) El nodo de tipo Nudo y nombre "Nudo Final". Se trata de un nudo al cual irán a parar todos los flujos
    # que salgan o escapen del sistema (esto es, que no se incorporen al mismo), y al que normalmente se le asignará el número
    # conceptual 0. Esto no significa que su identificador único de nodo sea 0; de hecho, en el ejemplo de la red hidrológica
    # del modelo SIMGES del PHDS1521, su identificador único es 106. Este indicador se define en el archivo de configuración
    # definido en la constante CONFIG_FILE, mediante el contenido de la columna CFSIFtdf_col_nombre_nodo_final.
    # A este nodo, una vez que se haya establecido el coste de todos los nodos a los que haya asignar un coste, le asignaremos
    # el valor máximo del coste de entre todas las posibles rutas que terminen en  este "Nodo Final" - 1.
    # Es decir: (-g_max_coste_ruta_nodo_final-1).
    #
    # (c) El nodo artificial que hemos generado por el momento para llevar todos los retornos: se trata del nodo "g_retorno_global".
    # A este nodo, una vez que se haya establecido el coste de todos los nodos a los que haya asignar un coste, le asignaremos
    # el valor máximo del coste de entre todas las posibles rutas que terminen en  este nodo "g_retorno_global" - 1.
    # Es decir: (-g_max_coste_ruta_nodo_retorno_global-1).
    #
    # (d) Los elementos / nodos de retorno de tipo Output. Se tratan los nodos en los que se registrarán los valores retornados que,
    # idealmente, tendrían que coincidir con las series que vayamos a definir para los elementos / nodos de retorno de tipo Input.
    # Con el fin de asegurar que posibles valores positivos impidan que el agua llegue a su destino (retorno_output), determinamos
    # el valor máximo del coste de entre todas las posibles rutas que terminen en un retorno (g_max_coste_ruta_retorno_output).
    # Así, al establecer el coste (beneficio) de los retornos, su valor base deberá ser (-g_max_coste_ruta_retornos_output-1).

    # (a) Empezamos por calcular g_max_coste_ruta_demandas

    coste_ruta = 0                # Inicialización
    g_max_coste_ruta_demandas = 0  # Inicialización

    # Lanzamos la búsqueda del valor g_max_coste_ruta_demandas
    for nodo in dic_demandas:
        mi_nodo = dic_demandas[nodo].parent
        if (mi_nodo == None):
            mi_nodo = dic_demandas[nodo]
        coste_ruta, g_max_coste_ruta_demandas = CalculateModelLargestCost(
            mi_nodo, coste_ruta, g_max_coste_ruta_demandas)

    # Ahora, para cada demanda, asignamos el valor (-g_max_coste_ruta_demandas-1) en su coste
    if (g_max_coste_ruta_demandas >= 0):
        coste = (-g_max_coste_ruta_demandas-1)*10
    for nodo in dic_demandas:
        dic_demandas[nodo].cost = coste

    # (b) Continuamos calculando g_max_coste_ruta_nodo_final

    coste_ruta = 0                   # Inicialización
    g_max_coste_ruta_nodo_final = 0  # Inicialización

    '''
    ### Determinamos el nodo "Nudo Final"
    g_ID_nodo_final = df_tpatdff[g_col_elemento_id][df_tpatdff[g_col_elemento_nombre]==g_nombre_nodo_final].values[0]
    g_nodo_final = dic_nudos[str(g_ID_nodo_final)]
    
    # Lanzamos la búsqueda del valor g_max_coste_ruta_nodo_final
    coste_ruta, g_max_coste_ruta_nodo_final = CalculateModelLargestCost(g_nodo_final, coste_ruta, g_max_coste_ruta_nodo_final)
    '''
    # Lanzamos la búsqueda del valor g_max_coste_ruta_nodo_final
    coste_ruta, g_max_coste_ruta_nodo_final = CalculateModelLargestCost(
        g_nudo_final, coste_ruta, g_max_coste_ruta_nodo_final)

    # Ahora, para g_nudo_final, asignamos el valor (-g_max_coste_ruta_nodo_final-1) en su coste
    # if (g_max_coste_ruta_nodo_final >= 0): coste = -g_max_coste_ruta_nodo_final-1
    if (g_max_coste_ruta_nodo_final <= 0):
        coste = -g_max_coste_ruta_nodo_final+1
    g_nudo_final.cost = coste

    # (c) Calculamos g_max_coste_ruta_nodo_retorno_global

    coste_ruta = 0                   # Inicialización
    g_max_coste_ruta_nodo_retorno_global = 0  # Inicialización

    # Lanzamos la búsqueda del valor g_max_coste_ruta_nodo_retorno_global
    coste_ruta, g_max_coste_ruta_nodo_retorno_global = CalculateModelLargestCost(
        g_retorno_global, coste_ruta, g_max_coste_ruta_nodo_retorno_global)

    # Ahora, para g_retorno_global, asignamos el valor (-g_max_coste_ruta_nodo_final-1) en su coste
    # if (g_max_coste_ruta_nodo_retorno_global >= 0): coste = -g_max_coste_ruta_nodo_retorno_global-1
    if (g_max_coste_ruta_nodo_retorno_global <= 0):
        coste = -g_max_coste_ruta_nodo_retorno_global+1
    g_retorno_global.cost = coste

    # (d) Calculamos g_max_coste_ruta_retornos_output

    coste_ruta = 0                       # Inicialización
    g_max_coste_ruta_retornos_output = 0  # Inicialización

    # Lanzamos la búsqueda del valor g_max_coste_ruta_retornos_output
    for nodo in dic_retornos_output:
        mi_nodo = dic_retornos_output[nodo].parent
        if (mi_nodo == None):
            mi_nodo = dic_retornos_output[nodo]
        coste_ruta, g_max_coste_ruta_retornos_output = CalculateModelLargestCost(
            mi_nodo, coste_ruta, g_max_coste_ruta_retornos_output)

    # Ahora, para cada rertorno_output, asignamos el valor (-g_max_coste_ruta_demandas-1) en su coste
    if (g_max_coste_ruta_retornos_output >= 0):
        coste = -g_max_coste_ruta_retornos_output-1
    for nodo in dic_retornos_output:
        dic_retornos_output[nodo].cost = coste

    '''
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    '''

    # In order to capture the output from the model we need to use recorders.

    # Recorders for (0) Nudo <---> Link
    # NOTA: el nodo cuyo nombre es "Nudo Final", debe ser creado como Output.
    #       Este nodo se guardará en la variable específica g_nudo_final.
    # Creamos recorders para g_nudo_final.

    recorder_g_nudo_final_flow = NumpyArrayNodeRecorder(
        model, g_nudo_final)  # Flow recorder
    # This class stores FLOW for each time-step of a simulation

    # Recorders for (1) Embalse <---> Storage
    recorder_embalses_volume = {}  # Volume recorder
    recorder_embalses_min_volume = {}  # Min volume recorder
    for embalse in dic_embalses:
        recorder_embalses_volume[embalse] = NumpyArrayStorageRecorder(
            model, dic_embalses[embalse])
        # This class stores VOLUME for each time-step of a simulation

        recorder_embalses_min_volume[embalse] = MinimumVolumeStorageRecorder(
            model, dic_embalses[embalse])
        # This class stores the MINIMUM VOLUME in a Storage node during a simulation

    # Recorders para (2) Aportacion <---> Input
    recorder_aportaciones_flow = {}  # Flow recorder
    for aportacion in dic_aportaciones:
        recorder_aportaciones_flow[aportacion] = NumpyArrayNodeRecorder(
            model, dic_aportaciones[aportacion])
        # This class stores FLOW for each time-step of a simulation

    # Recorders para (3) Demanda <---> Output
    recorder_demandas_flow = {}  # Flow recorder
    # Flow deficit occurring frequency recorder
    recorder_demandas_flow_deficit_frequency = {}
    for demanda in dic_demandas:
        recorder_demandas_flow[demanda] = NumpyArrayNodeRecorder(
            model, dic_demandas[demanda])
        # This class stores FLOW for each time-step of a simulation

        recorder_demandas_flow_deficit_frequency[demanda] = DeficitFrequencyNodeRecorder(
            model, dic_demandas[demanda])
        # This class stores FREQUENCY of TIMESTEPS with a failure to meet max_flow

    # Recorders para (4) Toma <---> MultiSplitLink
    recorder_tomas_flow = {}  # Flow recorder
    for toma in dic_tomas:
        recorder_tomas_flow[toma] = NumpyArrayNodeRecorder(
            model, dic_tomas[toma])
        # This class stores FLOW for each time-step of a simulation

    # Recorders para (5) Conduccion1 <---> LossLink
    recorder_conducciones1_flow = {}  # Flow recorder
    for conduccion1 in dic_conducciones1:
        recorder_conducciones1_flow[conduccion1] = NumpyArrayNodeRecorder(
            model, dic_conducciones1[conduccion1])
        # This class stores FLOW for each time-step of a simulation

    # Recorders para (6) Conduccion3 <---> LossLink
    recorder_conducciones3_flow = {}  # Flow recorder
    for conduccion3 in dic_conducciones3:
        recorder_conducciones3_flow[conduccion3] = NumpyArrayNodeRecorder(
            model, dic_conducciones3[conduccion3])
        # This class stores FLOW for each time-step of a simulation

    # Recorders para (7) Bombeo <---> Link
    recorder_bombeos_flow = {}  # Flow recorder
    for bombeo in dic_bombeos:
        recorder_bombeos_flow[bombeo] = NumpyArrayNodeRecorder(
            model, dic_bombeos[bombeo])
        # This class stores FLOW for each time-step of a simulation

    # Recorders para (8) Retorno <---> Input
    recorder_retornos_input_flow = {}  # Flow recorder
    for retorno_input in dic_retornos_input:
        recorder_retornos_input_flow[retorno_input] = NumpyArrayNodeRecorder(
            model, dic_retornos_input[retorno_input])
        # This class stores FLOW for each time-step of a simulation

    # Recorders para (8) Retorno <---> Output
    recorder_retornos_output_flow = {}  # Flow recorder
    # Flow deficit occurring frequency recorder
    recorder_retornos_output_flow_deficit_frequency = {}
    for retorno_output in dic_retornos_output:
        recorder_retornos_output_flow[retorno_output] = NumpyArrayNodeRecorder(
            model, dic_retornos_output[retorno_output])
        # This class stores FLOW for each time-step of a simulation

        recorder_retornos_output_flow_deficit_frequency[retorno_output] = DeficitFrequencyNodeRecorder(
            model, dic_retornos_output[retorno_output])
        # This class stores FREQUENCY of TIMESTEPS with a failure to meet max_flow

    # Recorders para (9) Acuifero <---> Input [+ Storage]
    recorder_acuiferos_flow = {}  # Flow recorder
    for acuifero in dic_acuiferos:
        recorder_acuiferos_flow[acuifero] = NumpyArrayNodeRecorder(
            model, dic_acuiferos[acuifero])
        # This class stores FLOW for each time-step of a simulation

    # Recorder para (10) RETORNO_GLOBAL <---> Output
    recorder_retorno_global_flow = NumpyArrayNodeRecorder(
        model, g_retorno_global)  # Flow recorder
    # This class stores FLOW for each time-step of a simulation

    '''
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    '''

    # Next we need to tell the model how long to run for

    # Define values.
    # Caso 1: SIMULATION_STEP_PASO_DIARIO
    if (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
        my_timedelta_in_days = 1
        n_simulation_steps = (pd.to_datetime(
            p_date_end) - pd.to_datetime(p_date_init)).days + 1
        simulation_step = "days"

        # IMPORTANTE: por provlemas con el Solver del pywr, no hemos conseguio simular más de MAX_N_MESES_SIMUL (9)
        # meses de tiempo. Por tanto, limitamos la simulación a este periodo.
        if (n_simulation_steps > (MAX_N_MESES_SIMUL * N_DIAS_MES_ESTANDAR)):
            p_date_end = (pd.to_datetime(p_date_init) + timedelta(
                days=(MAX_N_MESES_SIMUL * N_DIAS_MES_ESTANDAR))).strftime('%Y-%m-%d')

        # Define model.timestepper.
        model.timestepper = Timestepper(start=pd.to_datetime(p_date_init), end=pd.to_datetime(p_date_end),
                                        delta=timedelta(days=my_timedelta_in_days))

        # Finalmente, determinamos el día del año correspondiente a model.timestepper.start y
        # model.timestepper.end, porque los necesitaremos más adelante a la hora de guardas los resultados
        simul_start_day_of_year = model.timestepper.start.timetuple().tm_yday
        simul_end_day_of_year = model.timestepper.end.timetuple().tm_yday

    # Caso 2: SIMULATION_STEP_PASO_MENSUAL
    if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
        my_timedelta_in_days = N_DIAS_MES_ESTANDAR+1  # 31 días
        n_simulation_steps = (pd.Series(pd.to_datetime(p_date_end)).dt.to_period('M').view(dtype='int64') -
                              pd.Series(pd.to_datetime(p_date_init)).dt.to_period('M').view(dtype='int64')).values[0] + 1
        simulation_step = "months"

        # IMPORTANTE: por provlemas con el Solver del pywr, no hemos conseguio simular más de MAX_N_MESES_SIMUL (9)
        # meses de tiempo. Por tanto, limitamos la simulación a este periodo.
        if (n_simulation_steps > MAX_N_MESES_SIMUL):
            p_date_end = (pd.to_datetime(p_date_init) + timedelta(
                days=(MAX_N_MESES_SIMUL * N_DIAS_MES_ESTANDAR))).strftime('%Y-%m-%d')

        # Define model.timestepper.
        model.timestepper = Timestepper(start=pd.to_datetime(p_date_init), end=pd.to_datetime(p_date_end),
                                        delta=timedelta(days=my_timedelta_in_days))

        # Finalmente, determinamos el mes del año correspondiente a model.timestepper.start y
        # model.timestepper.end, porque los necesitaremos más adelante a la hora de guardas los resultados
        simul_start_month_of_year = model.timestepper.start.timetuple().tm_mon
        simul_end_month_of_year = model.timestepper.end.timetuple().tm_mon

    # Finally we are ready to run our model:
    # Lets get this party started!
    logging.debug("    Running simulation from %s to %s [%d %s]" % (
        p_date_init, p_date_end, n_simulation_steps, simulation_step))

    # Measure comnputation time (start time).
    start_t = time.time()

    # Antes de ejecutar el modelo, es necesario hacer model.setup() para quwe se carguen los parámetros
    # que se han cargado con el método paraneyter.load_paraemter()
    model.setup()

    # Run the model
    model.run()

    # Measure and print comnpotation time (end time)
    end_t = time.time()
    logging.debug("\nFINISHED. \nComputation time for simulating %d %s is %g seconds.\n" % (
        n_simulation_steps, simulation_step, (end_t - start_t)))

    '''
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    '''

    # Ver los datos en forma de dataframe. Imprimirlos y guardarlos a archivos.
    # Crearemos un df de resultados por cada tipo de nodo.

    # Obtener los datos de configuración
    df_config_out_file = xl_cf.parse(
        sheet_name=CF_SHEET_OUT_FILE, header=CFSOF_HEADER)

    # Calcular y guardar resultados a archivo.

    # Initializar variables que se utilizar para mostrar valores totales
    g_col_total_flow_aportaciones_all_prev = 0
    g_col_total_flow_retornos_input_all_prev = 0
    g_col_total_flow_retornos_output_all_prev = 0
    g_col_total_flow_acuiferos_all_prev = 0
    g_col_total_flow_INPUT_all_prev = 0
    g_col_total_flow_demandas_all_prev = 0
    g_col_total_flow_OUTPUT_all_prev = 0
    g_col_total_flow_aportaciones_all_real = 0
    g_col_total_flow_retornos_input_all_real = 0
    g_col_total_flow_retornos_output_all_real = 0
    g_col_total_flow_acuiferos_all_real = 0
    g_col_total_flow_INPUT_all_real = 0
    g_col_total_flow_demandas_all_real = 0
    g_col_total_flow_OUTPUT_all_real = 0

    # NOTA explicativa del uso del método ".aggregated_value()" de los recorders: lo que hace el agregado de la ventana temporal
    # de simulación:
    # + Si el recorder es "MeanFlowNodeRecorder", lo que hará ".aggregated_value()" será calcular el caudal MEDIO
    #   para ese elemento a lo largo de toda la simulación.
    # + Si el recorder es "TotalFlowNodeRecorder", lo que hará ".aggregated_value()" será calcular el caudal TOTAL
    #   para ese elemento a lo largo de toda la simulación.

    '''
    Calcular + guardar datos de recorders para (0) Nudo <---> Link
    NOTA: el nodo cuyo nombre es "Nudo Final", debe ser creado como Output.
          Este nodo se guardará en la variable específica g_nudo_final.
    '''

    # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
    df_results_nudo_final = recorder_g_nudo_final_flow.to_dataframe()
    df_results_nudo_final.columns = [
        df_config_out_file[CFSOF_col_flow].iloc[0]]
    df_results_nudo_final[df_config_out_file[CFSOF_col_mean_flow].iloc[0]
                          ] = df_results_nudo_final[df_config_out_file[CFSOF_col_flow].iloc[0]].mean()
    df_results_nudo_final[df_config_out_file[CFSOF_col_total_flow].iloc[0]
                          ] = df_results_nudo_final[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()
    df_results_nudo_final[df_config_out_file[CFSOF_col_id].iloc[0]
                          ] = g_nudo_final.name  # Node ID
    df_results_nudo_final[df_config_out_file[CFSOF_col_name].iloc[0]
                          ] = g_nudo_final.comment  # Node name (description)
    df_results_nudo_final[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                          ] = df_results_nudo_final.index  # Timestamp

    # Reorder columns
    # columnas = df_results_nudo_final.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0], df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0], df_config_out_file[CFSOF_col_total_flow].iloc[0]]

    df_results_nudo_final = df_results_nudo_final[columnas]
    df_results_nudo_final.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (1) Embalse <---> Storage
    '''

    primer_nodo = list(dic_embalses.keys())[0]
    for embalse in dic_embalses:
        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_embalse = recorder_embalses_volume[embalse].to_dataframe()
        df_results_embalse.columns = [
            df_config_out_file[CFSOF_col_volume].iloc[0]]
        # Node ID
        df_results_embalse[df_config_out_file[CFSOF_col_id].iloc[0]] = embalse
        df_results_embalse[df_config_out_file[CFSOF_col_name].iloc[0]
                           ] = dic_embalses[embalse].comment  # Node name (description)
        df_results_embalse[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                           ] = df_results_embalse.index  # Timestamp
        df_results_embalse[df_config_out_file[CFSOF_col_min_volume].iloc[0]
                           ] = recorder_embalses_min_volume[embalse].aggregated_value()

        # Initial(ised) data columns
        # Datos que vienen de series (parámetros)
        df_results_embalse[df_config_out_file[CFSOF_col_init_vol].iloc[0]
                           ] = dic_embalses[embalse].initial_volume  # Initial volume
    # MIKEL: por el momento, los siguientes dos datos no los gestionamos en forma de parámetros porque no conseguimos sacarlos.
    #     df_results_embalse[df_config_out_file[CFSOF_col_init_min_vol].iloc[0]] = dic_embalses[embalse].min_volume # Initial min volume
    #     df_results_embalse[df_config_out_file[CFSOF_col_init_max_vol].iloc[0]] = dic_embalses[embalse].max_volume # Initial min volume

        # SOLUCION: utilizamos los df de parámetros creados en la fase de inicio:
        # Serie de valores de vol_min y vol_max definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de vol_min
            df_all_values_element = df_PARAMS_EMBALSES_vol_min_mensual[[
                dic_embalses[embalse].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
            df_results_embalse[df_config_out_file[CFSOF_col_init_min_vol].iloc[0]
                               ] = df_list_values_simulation.values

            # Serie de valores de vol_max
            df_all_values_element = df_PARAMS_EMBALSES_vol_max_mensual[[
                dic_embalses[embalse].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
            df_results_embalse[df_config_out_file[CFSOF_col_init_max_vol].iloc[0]
                               ] = df_list_values_simulation.values
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de vol_min
            df_all_values_element = df_PARAMS_EMBALSES_vol_min_diario[[
                dic_embalses[embalse].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]
            df_results_embalse[df_config_out_file[CFSOF_col_init_min_vol].iloc[0]
                               ] = df_list_values_simulation.values

            # Serie de valores de vol_max
            df_all_values_element = df_PARAMS_EMBALSES_vol_max_diario[[
                dic_embalses[embalse].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]
            df_results_embalse[df_config_out_file[CFSOF_col_init_max_vol].iloc[0]
                               ] = df_list_values_simulation.values

        # Continuamos con otros valores que no vienen de parámetros (no son series)
        df_results_embalse[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                           ] = dic_embalses[embalse].max_flow  # (Initial) max flow
        df_results_embalse[df_config_out_file[CFSOF_col_cost].iloc[0]
                           ] = dic_embalses[embalse].cost  # (Initial) cost

        # Actualizar el df con la info de todos los embalses
        if (embalse == primer_nodo):
            df_results_embalses = df_results_embalse.copy()
        else:
            df_results_embalses = pd.concat(
                [df_results_embalses, df_results_embalse.copy()], ignore_index=True)

    # Reorder columns
    # columnas = df_results_embalses.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0], df_config_out_file[CFSOF_col_cost].iloc[0],
                df_config_out_file[CFSOF_col_init_vol].iloc[0], df_config_out_file[CFSOF_col_init_min_vol].iloc[0],
                df_config_out_file[CFSOF_col_init_max_vol].iloc[0], df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_volume].iloc[0], df_config_out_file[CFSOF_col_min_volume].iloc[0]]

    df_results_embalses = df_results_embalses[columnas]
    df_results_embalses.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (2) Aportacion <---> Input
    '''

    primer_nodo = list(dic_aportaciones.keys())[0]
    for aportacion in dic_aportaciones:
        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_aportacion = recorder_aportaciones_flow[aportacion].to_dataframe(
        )
        df_results_aportacion.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_aportacion[df_config_out_file[CFSOF_col_id].iloc[0]] = aportacion
        df_results_aportacion[df_config_out_file[CFSOF_col_name].iloc[0]
                              ] = dic_aportaciones[aportacion].comment  # Node name (description)
        df_results_aportacion[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                              ] = df_results_aportacion.index  # Timestamp
        df_results_aportacion[df_config_out_file[CFSOF_col_mean_flow].iloc[0]
                              ] = df_results_aportacion[df_config_out_file[CFSOF_col_flow].iloc[0]].mean()
        df_results_aportacion[df_config_out_file[CFSOF_col_total_flow].iloc[0]
                              ] = df_results_aportacion[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()

        # Initial(ised) data columns
        # Datos que vienen de series (parámetros)
    # MIKEL: por el momento, los siguientes dos datos no los gestionamos en forma de parámetros porque no conseguimos sacarlos.
    #     df_results_aportacion[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] = dic_aportaciones[aportacion].max_flow # (Initial) max flow

        # SOLUCION: utilizamos los df de parámetros a cargar a partir de los archivos de aportaciones:
        nombre_aportacion = dic_aportaciones[aportacion].comment

        # Determinamos la columna en el archivo de aportaciones
        columna_en_archivo_aportaciones = \
            df_pdf_aportaciones[[CFSDA_col_columna_en_archivo_aportaciones]
                                ][df_pdf_aportaciones[CFSDA_col_nombre] == '"' + nombre_aportacion + '"'].iloc[0].values[0]

        # Determinamos el nombre del archivo de aportaciones, abrimos el archivo y obtenemos los datos que nos interesan:
        # Nombre de archivo
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):  # Simulación de paso mensual
            file_name_aportaciones = PARAMETROS_APORTACIONES_DIRECTORIO_MENSUAL + PREFIJO_ARCHIVO_CSV_APORTACIONES_MENSUAL + \
                str(columna_en_archivo_aportaciones) + '.csv'

        else:  # Simulación de paso diario
            file_name_aportaciones = PARAMETROS_APORTACIONES_DIRECTORIO_DIARIO + PREFIJO_ARCHIVO_CSV_APORTACIONES_DIARIO + \
                str(columna_en_archivo_aportaciones) + '.csv'

        # Abrir archivo
        df_all_values_element = pd.read_csv(file_name_aportaciones)

        # Obtener los datos que nos interesan
        df_list_values_simulation = df_all_values_element[
            df_all_values_element[ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA] >= p_date_init]
        df_list_values_simulation = df_list_values_simulation[
            df_list_values_simulation[ARCHIVO_CSV_APORTACIONES_CAMPO_FECHA] <= p_date_end]

        # Asignar los valores
        df_results_aportacion[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] = \
            df_list_values_simulation[ARCHIVO_CSV_APORTACIONES_CAMPO_VALOR].values

        # Seguimos con otros calculos
        df_results_aportacion[df_config_out_file[CFSOF_col_flow_supplied_rate].iloc[0]] = \
            df_results_aportacion[df_config_out_file[CFSOF_col_flow].iloc[0]] / \
            df_results_aportacion[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]]

        df_results_aportacion[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] = \
            df_results_aportacion[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
        )
        df_results_aportacion[df_config_out_file[CFSOF_col_total_flow_supplied_rate].iloc[0]] = \
            df_results_aportacion[df_config_out_file[CFSOF_col_total_flow].iloc[0]] / \
            df_results_aportacion[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]]

        # Actualizar el df con la info de todas las aportaciones
        if (aportacion == primer_nodo):
            df_results_aportaciones = df_results_aportacion.copy()
        else:
            df_results_aportaciones = pd.concat(
                [df_results_aportaciones, df_results_aportacion.copy()], ignore_index=True)

    # Calcular datos agregados totales
    df_results_aportaciones[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_real].iloc[0]] = \
        df_results_aportaciones[df_config_out_file[CFSOF_col_flow].iloc[0]].sum(
    )
    g_col_total_flow_aportaciones_all_real = \
        df_results_aportaciones[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_real].iloc[0]].values[0]

    df_results_aportaciones[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_prev].iloc[0]] = \
        df_results_aportaciones[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
    )
    g_col_total_flow_aportaciones_all_prev = \
        df_results_aportaciones[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_prev].iloc[0]].values[0]

    df_results_aportaciones[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_supplied_rate].iloc[0]] = \
        g_col_total_flow_aportaciones_all_real / g_col_total_flow_aportaciones_all_prev
    g_col_total_flow_aportaciones_all_supplied_rate = \
        df_results_aportaciones[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_supplied_rate].iloc[0]].values[0]

    # Reorder columns
    # columnas = df_results_aportaciones.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_flow_supplied_rate].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_supplied_rate].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_aportaciones_all_real].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_aportaciones_all_prev].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_aportaciones_all_supplied_rate].iloc[0]]

    df_results_aportaciones = df_results_aportaciones[columnas]
    df_results_aportaciones.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (3) Demanda <---> Output")
    '''

    primer_nodo = list(dic_demandas.keys())[0]
    for demanda in dic_demandas:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_demanda = recorder_demandas_flow[demanda].to_dataframe()
        df_results_demanda.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_demanda[df_config_out_file[CFSOF_col_id].iloc[0]] = demanda
        df_results_demanda[df_config_out_file[CFSOF_col_name].iloc[0]
                           ] = dic_demandas[demanda].comment  # Node name (description)
        df_results_demanda[g_col_demanda_tipo] = df_demandas[df_demandas[g_col_elemento_id] == int(
            demanda)][g_col_demanda_tipo].values[0]  # Tipo de demanda
        df_results_demanda[g_col_demanda_tipo_nombre] = df_demandas[df_demandas[g_col_elemento_id] == int(
            demanda)][g_col_demanda_tipo_nombre].values[0]  # Nombre del tipo de demanda
        df_results_demanda[g_col_demanda_mi_id] = df_demandas[df_demandas[g_col_elemento_id] == int(
            demanda)][g_col_demanda_mi_id].values[0]  # ID de demanda que utilizamos en la plataforma
        df_results_demanda[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                           ] = df_results_demanda.index  # Timestamp
        df_results_demanda[df_config_out_file[CFSOF_col_mean_flow].iloc[0]
                           ] = df_results_demanda[df_config_out_file[CFSOF_col_flow].iloc[0]].mean()
        df_results_demanda[df_config_out_file[CFSOF_col_total_flow].iloc[0]
                           ] = df_results_demanda[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()
        df_results_demanda[df_config_out_file[CFSOF_col_flow_deficit_frequency].iloc[0]
                           ] = recorder_demandas_flow_deficit_frequency[demanda].aggregated_value()

        # Initial(ised) data columns
    # MIKEL: por el momento, los siguientes dos datos no los gestionamos en forma de parámetros porque no conseguimos sacarlos.
    #     df_results_demanda[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] = dic_demandas[demanda].max_flow # (Initial) max flow

        # SOLUCION: utilizamos los df de parámetros creados en la fase de inicio:
        # Serie de valores de demanda definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de demanda
            df_all_values_element = df_PARAMS_DEMANDAS_mensual[[
                dic_demandas[demanda].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de demanda
            df_all_values_element = df_PARAMS_DEMANDAS_diario[[
                dic_demandas[demanda].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]

        # Asignar los valores
        df_results_demanda[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                           ] = df_list_values_simulation.values

        # Seguimos con otros cálculos
        df_results_demanda[df_config_out_file[CFSOF_col_flow_deficit].iloc[0]] = \
            df_results_demanda[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                               ] - df_results_demanda[df_config_out_file[CFSOF_col_flow].iloc[0]]

        # Calculamos y guardamos el déficit en forma de %
        # Por paso de simulación
        try:
            df_results_demanda[df_config_out_file[CFSOF_col_flow_deficit_percent].iloc[0]] = \
                df_results_demanda[df_config_out_file[CFSOF_col_flow_deficit].iloc[0]] / \
                df_results_demanda[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] * 100

        except:
            df_results_demanda[df_config_out_file[CFSOF_col_flow_deficit_percent].iloc[0]] = 100

        # Para la simulación completa
        df_results_demanda[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] = \
            df_results_demanda[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
        )
        df_results_demanda[df_config_out_file[CFSOF_col_total_flow_deficit].iloc[0]] = \
            df_results_demanda[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]
                               ] - df_results_demanda[df_config_out_file[CFSOF_col_total_flow].iloc[0]]

        # Para la simulación completa
        try:
            df_results_demanda[df_config_out_file[CFSOF_col_total_flow_deficit_percent].iloc[0]] = \
                df_results_demanda[df_config_out_file[CFSOF_col_total_flow_deficit].iloc[0]] / \
                df_results_demanda[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] * 100

        except:
            df_results_demanda[df_config_out_file[CFSOF_col_total_flow_deficit_percent].iloc[0]] = 100

        # Seguimos. Este valor de inicialización NO es un parámetro-serie-array.
        df_results_demanda[df_config_out_file[CFSOF_col_cost].iloc[0]
                           ] = dic_demandas[demanda].cost  # (Initial) cost

        # Actualizar el df con la info de todas las demandas
        if (demanda == primer_nodo):
            df_results_demandas = df_results_demanda.copy()
        else:
            df_results_demandas = pd.concat(
                [df_results_demandas, df_results_demanda.copy()], ignore_index=True)

    # Calcular datos agregados totales
    df_results_demandas[df_config_out_file[CFSOF_col_total_flow_demandas_all_real].iloc[0]
                        ] = df_results_demandas[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()
    g_col_total_flow_demandas_all_real = df_results_demandas[
        df_config_out_file[CFSOF_col_total_flow_demandas_all_real].iloc[0]].values[0]

    df_results_demandas[df_config_out_file[CFSOF_col_total_flow_demandas_all_prev].iloc[0]
                        ] = df_results_demandas[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum()
    g_col_total_flow_demandas_all_prev = df_results_demandas[
        df_config_out_file[CFSOF_col_total_flow_demandas_all_prev].iloc[0]].values[0]

    df_results_demandas[df_config_out_file[CFSOF_col_total_flow_demandas_all_deficit_percent].iloc[0]] = \
        (g_col_total_flow_demandas_all_prev - g_col_total_flow_demandas_all_real) / \
        g_col_total_flow_demandas_all_prev * 100
    g_col_total_flow_demandas_all_deficit_percent = df_results_demandas[
        df_config_out_file[CFSOF_col_total_flow_demandas_all_deficit_percent].iloc[0]].values[0]

    # Reorder columns
    # columnas = df_results_demandas.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                g_col_demanda_tipo,
                g_col_demanda_tipo_nombre,
                g_col_demanda_mi_id,
                df_config_out_file[CFSOF_col_cost].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_flow_deficit].iloc[0],
                df_config_out_file[CFSOF_col_flow_deficit_percent].iloc[0],
                df_config_out_file[CFSOF_col_flow_deficit_frequency].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_deficit].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_deficit_percent].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_demandas_all_real].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_demandas_all_prev].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_demandas_all_deficit_percent].iloc[0]]

    df_results_demandas = df_results_demandas[columnas]
    df_results_demandas.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de recorders para (4) Toma <---> MultiSplitLink
    Nota: en esta parte, se guardarán los datos que van por el lado de 'split_demanda', es decir, factors[0]
    '''

    primer_nodo = list(dic_tomas.keys())[0]
    for toma in dic_tomas:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_toma = recorder_tomas_flow[toma].to_dataframe()
        df_results_toma.columns = [df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Aplicamos el factor de consumo / demanda (.factors[0])
        df_results_toma[df_config_out_file[CFSOF_col_flow].iloc[0]
                        ] *= dic_tomas[toma].factors[0]

        # Continuamos
        # Node ID
        df_results_toma[df_config_out_file[CFSOF_col_id].iloc[0]] = toma
        df_results_toma[df_config_out_file[CFSOF_col_name].iloc[0]
                        ] = dic_tomas[toma].comment  # Node name (description)
        df_results_toma[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                        ] = df_results_toma.index  # Timestamp

        df_results_toma[df_config_out_file[CFSOF_col_mean_flow].iloc[0]
                        ] = df_results_toma[df_config_out_file[CFSOF_col_flow].iloc[0]].mean()

        df_results_toma[df_config_out_file[CFSOF_col_total_flow].iloc[0]
                        ] = df_results_toma[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()

        # Initial(ised) data columns
        df_results_toma[df_config_out_file[CFSOF_col_split_factor_demanda].iloc[0]
                        ] = dic_tomas[toma].factors[0]  # Split demanda
        df_results_toma[df_config_out_file[CFSOF_col_split_factor_retorno].iloc[0]
                        ] = dic_tomas[toma].factors[1]  # Split retorno

        # Actualizar el df con la info de todas las tomas
        if (toma == primer_nodo):
            df_results_tomas = df_results_toma.copy()
        else:
            df_results_tomas = pd.concat(
                [df_results_tomas, df_results_toma.copy()], ignore_index=True)

    # Valores agregados
    df_results_tomas[df_config_out_file[CFSOF_col_total_flow_tomas_all_real].iloc[0]] = \
        df_results_tomas[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()

    # Reorder columns
    # columnas = df_results_tomas.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_split_factor_demanda].iloc[0],
                df_config_out_file[CFSOF_col_split_factor_retorno].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_tomas_all_real].iloc[0]]

    df_results_tomas = df_results_tomas[columnas]
    df_results_tomas.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (5) Conduccion1 <---> LossLink
    '''

    primer_nodo = list(dic_conducciones1.keys())[0]
    for conduccion1 in dic_conducciones1:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_conduccion1 = recorder_conducciones1_flow[conduccion1].to_dataframe(
        )
        df_results_conduccion1.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_conduccion1[df_config_out_file[CFSOF_col_id].iloc[0]] = conduccion1
        df_results_conduccion1[df_config_out_file[CFSOF_col_name].iloc[0]
                               ] = dic_conducciones1[conduccion1].comment  # Node name (description)
        df_results_conduccion1[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                               ] = df_results_conduccion1.index  # Timestamp

        # Initial(ised) data columns
        df_results_conduccion1[df_config_out_file[CFSOF_col_conduccion_factor_perdida].iloc[0]] = \
            dic_conducciones1[conduccion1].loss_factor  # Factor de pérdida
    #     dic_conducciones1[conduccion1].loss_factor.get_constant_value() # Factor de pérdida; hay que sacarlo así solamente si
    #                                                                       al crear el nodo de tipo LossLink que es conduccion1
    #                                                                       se pasa como parámetro el valor de loss_factor

        # Serie de valores de q_min y q_max definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de q_min
            df_all_values_element = df_PARAMS_CONDUCCIONES1_q_min_mensual[[
                dic_conducciones1[conduccion1].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
            df_results_conduccion1[df_config_out_file[CFSOF_col_init_min_flow].iloc[0]
                                   ] = df_list_values_simulation.values

            # Serie de valores de q_max
            df_all_values_element = df_PARAMS_CONDUCCIONES1_q_max_mensual[[
                dic_conducciones1[conduccion1].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
            df_results_conduccion1[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                                   ] = df_list_values_simulation.values
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de q_min
            df_all_values_element = df_PARAMS_CONDUCCIONES1_q_min_diario[[
                dic_conducciones1[conduccion1].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]
            df_results_conduccion1[df_config_out_file[CFSOF_col_init_min_flow].iloc[0]
                                   ] = df_list_values_simulation.values

            # Serie de valores de q_max
            df_all_values_element = df_PARAMS_CONDUCCIONES1_q_max_diario[[
                dic_conducciones1[conduccion1].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]
            df_results_conduccion1[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                                   ] = df_list_values_simulation.values

        # Actualizar el df con la info de todas las conducciones1
        if (conduccion1 == primer_nodo):
            df_results_conducciones1 = df_results_conduccion1.copy()
        else:
            df_results_conducciones1 = pd.concat(
                [df_results_conducciones1, df_results_conduccion1.copy()], ignore_index=True)

    # Reorder columns
    # columnas = df_results_conducciones1.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_init_min_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_conduccion_factor_perdida].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0]]

    df_results_conducciones1 = df_results_conducciones1[columnas]
    df_results_conducciones1.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (6) Conduccion3 <---> LossLink
    '''

    primer_nodo = list(dic_conducciones3.keys())[0]
    for conduccion3 in dic_conducciones3:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_conduccion3 = recorder_conducciones3_flow[conduccion3].to_dataframe(
        )
        df_results_conduccion3.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_conduccion3[df_config_out_file[CFSOF_col_id].iloc[0]] = conduccion3
        df_results_conduccion3[df_config_out_file[CFSOF_col_name].iloc[0]
                               ] = dic_conducciones3[conduccion3].comment  # Node name (description)
        df_results_conduccion3[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                               ] = df_results_conduccion3.index  # Timestamp

        # Initial(ised) data columns
    # MIKEL: hago el cambio que se ve a continuación porque .get_constant_value() no me funciona
        df_results_conduccion3[df_config_out_file[CFSOF_col_conduccion_factor_perdida].iloc[0]] = \
            dic_conducciones3[conduccion3].loss_factor  # Factor de pérdida
    #     dic_conducciones3[conduccion3].loss_factor.get_constant_value() # Factor de pérdida; hay que sacarlo así solamente si
    #                                                                       al crear el nodo de tipo LossLink que es conduccion3
    #                                                                       se pasa como parámetro el valor de loss_factor

        # Serie de valores de q_min y q_max definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de q_min
            df_all_values_element = df_PARAMS_CONDUCCIONES3_q_min_mensual[[
                dic_conducciones3[conduccion3].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
            df_results_conduccion3[df_config_out_file[CFSOF_col_init_min_flow].iloc[0]
                                   ] = df_list_values_simulation.values

            # Serie de valores de q_max
            df_all_values_element = df_PARAMS_CONDUCCIONES3_q_max_mensual[[
                dic_conducciones3[conduccion3].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
            df_results_conduccion3[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                                   ] = df_list_values_simulation.values
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de q_min
            df_all_values_element = df_PARAMS_CONDUCCIONES3_q_min_diario[[
                dic_conducciones3[conduccion3].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]
            df_results_conduccion3[df_config_out_file[CFSOF_col_init_min_flow].iloc[0]
                                   ] = df_list_values_simulation.values

            # Serie de valores de q_max
            df_all_values_element = df_PARAMS_CONDUCCIONES3_q_max_diario[[
                dic_conducciones3[conduccion3].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]
            df_results_conduccion3[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                                   ] = df_list_values_simulation.values

        # Actualizar el df con la info de todas las conducciones3
        if (conduccion3 == primer_nodo):
            df_results_conducciones3 = df_results_conduccion3.copy()
        else:
            df_results_conducciones3 = pd.concat(
                [df_results_conducciones3, df_results_conduccion3.copy()], ignore_index=True)

    # Reorder columns
    # columnas = df_results_conducciones3.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_init_min_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_conduccion_factor_perdida].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0]]

    df_results_conducciones3 = df_results_conducciones3[columnas]
    df_results_conducciones3.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (7) Bombeo <---> Link")
    '''

    primer_nodo = list(dic_bombeos.keys())[0]
    for bombeo in dic_bombeos:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_bombeo = recorder_bombeos_flow[bombeo].to_dataframe()
        df_results_bombeo.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_bombeo[df_config_out_file[CFSOF_col_id].iloc[0]] = bombeo
        df_results_bombeo[df_config_out_file[CFSOF_col_name].iloc[0]
                          ] = dic_bombeos[bombeo].comment  # Node name (description)
        df_results_bombeo[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                          ] = df_results_bombeo.index  # Timestamp

        # Initial(ised) data columns
        df_results_bombeo[df_config_out_file[CFSOF_col_cost].iloc[0]
                          ] = dic_bombeos[bombeo].cost  # (Initial) cost

        # Actualizar el df con la info de todos los bombeos
        if (bombeo == primer_nodo):
            df_results_bombeos = df_results_bombeo.copy()
        else:
            df_results_bombeos = pd.concat(
                [df_results_bombeos, df_results_bombeo.copy()], ignore_index=True)

    # Calcular datos agregados totales
    df_results_bombeos[df_config_out_file[CFSOF_col_total_flow_bombeos_all_real].iloc[0]] = \
        df_results_bombeos[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()

    # Reorder columns
    # columnas = df_results_bombeos.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_cost].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_bombeos_all_real].iloc[0]]

    df_results_bombeos = df_results_bombeos[columnas]
    df_results_bombeos.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (8) Retorno <---> Input
    '''

    primer_nodo = list(dic_retornos_input.keys())[0]
    for retorno_input in dic_retornos_input:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_retorno_input = recorder_retornos_input_flow[retorno_input].to_dataframe(
        )
        df_results_retorno_input.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_retorno_input[df_config_out_file[CFSOF_col_id].iloc[0]
                                 ] = retorno_input
        df_results_retorno_input[df_config_out_file[CFSOF_col_name].iloc[0]
                                 ] = dic_retornos_input[retorno_input].comment  # Node name (description)
        df_results_retorno_input[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                                 ] = df_results_retorno_input.index  # Timestamp
        df_results_retorno_input[df_config_out_file[CFSOF_col_mean_flow].iloc[0]
                                 ] = df_results_retorno_input[df_config_out_file[CFSOF_col_flow].iloc[0]].mean()
        df_results_retorno_input[df_config_out_file[CFSOF_col_total_flow].iloc[0]
                                 ] = df_results_retorno_input[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()

        # Initial(ised) data columns
    # MIKEL: por el momento, los siguientes dos datos no los gestionamos en forma de parámetros porque no conseguimos sacarlos.
    #     df_results_retorno_input[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] = dic_retornos_input[retorno_input].max_flow # (Initial) max flow

        # SOLUCION: utilizamos los df de parámetros creados en la fase de inicio:
        # Serie de valores de retorno_input definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de retorno_input
            df_all_values_element = df_PARAMS_RETORNOS_demanda_mensual[[
                dic_retornos_input[retorno_input].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de retorno_input
            df_all_values_element = df_PARAMS_RETORNOS_demanda_diario[[
                dic_retornos_input[retorno_input].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]

        # Asignar los valores
        df_results_retorno_input[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                                 ] = df_list_values_simulation.values

        # Seguimos con otros cálculos
        df_results_retorno_input[df_config_out_file[CFSOF_col_flow_supplied_rate].iloc[0]] = \
            df_results_retorno_input[df_config_out_file[CFSOF_col_flow].iloc[0]] / \
            df_results_retorno_input[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]]

        df_results_retorno_input[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] = \
            df_results_retorno_input[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
        )  # Total (initial) max flow
        df_results_retorno_input[df_config_out_file[CFSOF_col_total_flow_supplied_rate].iloc[0]] = \
            df_results_retorno_input[df_config_out_file[CFSOF_col_total_flow].iloc[0]] / \
            df_results_retorno_input[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]]

        # Seguimos con otros valores que no requieren cálculo
        df_results_retorno_input[df_config_out_file[CFSOF_col_cost].iloc[0]
                                 ] = dic_retornos_input[retorno_input].cost  # (Initial) cost

        # Actualizar el df con la info de todos los retornos
        if (retorno_input == primer_nodo):
            df_results_retornos_input = df_results_retorno_input.copy()
        else:
            df_results_retornos_input = pd.concat(
                [df_results_retornos_input, df_results_retorno_input.copy()], ignore_index=True)

    # Calcular datos agregados totales
    df_results_retornos_input[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_real].iloc[0]] = \
        df_results_retornos_input[df_config_out_file[CFSOF_col_flow].iloc[0]].sum(
    )
    g_col_total_flow_retornos_input_all_real = \
        df_results_retornos_input[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_real].iloc[0]].values[0]

    df_results_retornos_input[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_prev].iloc[0]] = \
        df_results_retornos_input[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
    )
    g_col_total_flow_retornos_input_all_prev = \
        df_results_retornos_input[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_prev].iloc[0]].values[0]

    df_results_retornos_input[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_supplied_rate].iloc[0]] = \
        g_col_total_flow_retornos_input_all_real / \
        g_col_total_flow_retornos_input_all_prev
    g_col_total_flow_retornos_input_all_supplied_rate = \
        df_results_retornos_input[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_supplied_rate].iloc[0]].values[0]

    # Reorder columns
    # columnas = df_results_retornos_input.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_cost].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_flow_supplied_rate].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_supplied_rate].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_retornos_input_all_real].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_retornos_input_all_prev].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_retornos_input_all_supplied_rate].iloc[0]]

    df_results_retornos_input = df_results_retornos_input[columnas]
    df_results_retornos_input.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (8) Retorno <---> Output
    '''

    primer_nodo = list(dic_retornos_output.keys())[0]
    for retorno_output in dic_retornos_output:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_retorno_output = recorder_retornos_output_flow[retorno_output].to_dataframe(
        )
        df_results_retorno_output.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_retorno_output[df_config_out_file[CFSOF_col_id].iloc[0]
                                  ] = retorno_output
        df_results_retorno_output[df_config_out_file[CFSOF_col_name].iloc[0]
                                  ] = dic_retornos_output[retorno_output].comment  # Node name (description)
        df_results_retorno_output[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                                  ] = df_results_retorno_output.index  # Timestamp
        df_results_retorno_output[df_config_out_file[CFSOF_col_mean_flow].iloc[0]] = \
            df_results_retorno_output[df_config_out_file[CFSOF_col_flow].iloc[0]].mean(
        )
        df_results_retorno_output[df_config_out_file[CFSOF_col_total_flow].iloc[0]] = \
            df_results_retorno_output[df_config_out_file[CFSOF_col_flow].iloc[0]].sum(
        )
        df_results_retorno_output[df_config_out_file[CFSOF_col_flow_deficit_frequency].iloc[0]] = \
            recorder_retornos_output_flow_deficit_frequency[retorno_output].aggregated_value(
        )

        # Initial(ised) data columns
    # MIKEL: por el momento, los siguientes dos datos no los gestionamos en forma de parámetros porque no conseguimos sacarlos.
    #     df_results_retorno_output[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] = dic_retornos_output[retorno_output].max_flow # (Initial) max flow

        # SOLUCION: utilizamos los df de parámetros creados en la fase de inicio:
        # Serie de valores de retorno_output definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de retorno_output
            df_all_values_element = df_PARAMS_RETORNOS_demanda_mensual[[
                dic_retornos_output[retorno_output].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de retorno_output
            df_all_values_element = df_PARAMS_RETORNOS_demanda_diario[[
                dic_retornos_output[retorno_output].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]

        # Asignar los valores
        df_results_retorno_output[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                                  ] = df_list_values_simulation.values

        # Seguimos con otros cálculos
        df_results_retorno_output[df_config_out_file[CFSOF_col_flow_deficit].iloc[0]] = \
            df_results_retorno_output[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] - \
            df_results_retorno_output[df_config_out_file[CFSOF_col_flow].iloc[0]]

        # Calculamos y guardamos el déficit en forma de %
        # Por paso de simulación
        try:
            df_results_retorno_output[df_config_out_file[CFSOF_col_flow_deficit_percent].iloc[0]] = \
                df_results_retorno_output[df_config_out_file[CFSOF_col_flow_deficit].iloc[0]] / \
                df_results_retorno_output[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] * 100

        except:
            df_results_retorno_output[df_config_out_file[CFSOF_col_flow_deficit_percent].iloc[0]] = 100

        # Para la simulación completa
        df_results_retorno_output[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] = \
            df_results_retorno_output[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
        )
        df_results_retorno_output[df_config_out_file[CFSOF_col_total_flow_deficit].iloc[0]] = \
            df_results_retorno_output[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] - \
            df_results_retorno_output[df_config_out_file[CFSOF_col_total_flow].iloc[0]]

        # Para la simulación completa
        try:
            df_results_retorno_output[df_config_out_file[CFSOF_col_total_flow_deficit_percent].iloc[0]] = \
                df_results_retorno_output[df_config_out_file[CFSOF_col_total_flow_deficit].iloc[0]] / \
                df_results_retorno_output[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] * 100

        except:
            df_results_retorno_output[df_config_out_file[CFSOF_col_total_flow_deficit_percent].iloc[0]] = 100

        # Seguimos. Este valor de inicialización NO es un parámetro-serie-array.
        df_results_retorno_output[df_config_out_file[CFSOF_col_cost].iloc[0]
                                  ] = dic_demandas[demanda].cost  # (Initial) cost

        # Actualizar el df con la info de todas las retornos_output
        if (retorno_output == primer_nodo):
            df_results_retornos_output = df_results_retorno_output.copy()
        else:
            df_results_retornos_output = pd.concat(
                [df_results_retornos_output, df_results_retorno_output.copy()], ignore_index=True)

    # Calcular datos agregados totales
    df_results_retornos_output[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_real].iloc[0]] = \
        df_results_retornos_output[df_config_out_file[CFSOF_col_flow].iloc[0]].sum(
    )
    g_col_total_flow_retornos_output_all_real = \
        df_results_retornos_output[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_real].iloc[0]].values[0]

    df_results_retornos_output[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_prev].iloc[0]] = \
        df_results_retornos_output[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
    )
    g_col_total_flow_retornos_output_all_prev = \
        df_results_retornos_output[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_prev].iloc[0]].values[0]

    df_results_retornos_output[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_deficit_percent].iloc[0]] = \
        (g_col_total_flow_retornos_output_all_prev - g_col_total_flow_retornos_output_all_real) / \
        g_col_total_flow_retornos_output_all_prev * 100
    g_col_total_flow_retornos_output_all_deficit_percent = \
        df_results_retornos_output[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_deficit_percent].iloc[0]].values[0]

    # Reorder columns
    # columnas = df_results_retornos_output.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_cost].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_flow_deficit].iloc[0],
                df_config_out_file[CFSOF_col_flow_deficit_percent].iloc[0],
                df_config_out_file[CFSOF_col_flow_deficit_frequency].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_deficit].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_deficit_percent].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_retornos_output_all_real].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_retornos_output_all_prev].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_retornos_output_all_deficit_percent].iloc[0]]

    df_results_retornos_output = df_results_retornos_output[columnas]
    df_results_retornos_output.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (9) Acuifero <---> Input [+ Storage]
    '''

    primer_nodo = list(dic_acuiferos.keys())[0]
    for acuifero in dic_acuiferos:

        # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
        df_results_acuifero = recorder_acuiferos_flow[acuifero].to_dataframe()
        df_results_acuifero.columns = [
            df_config_out_file[CFSOF_col_flow].iloc[0]]
        # Node ID
        df_results_acuifero[df_config_out_file[CFSOF_col_id].iloc[0]] = acuifero
        df_results_acuifero[df_config_out_file[CFSOF_col_name].iloc[0]
                            ] = dic_acuiferos[acuifero].comment  # Node name (description)
        df_results_acuifero[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                            ] = df_results_acuifero.index  # Timestamp
        df_results_acuifero[df_config_out_file[CFSOF_col_mean_flow].iloc[0]] = \
            df_results_acuifero[df_config_out_file[CFSOF_col_flow].iloc[0]].mean(
        )
        df_results_acuifero[df_config_out_file[CFSOF_col_total_flow].iloc[0]] = \
            df_results_acuifero[df_config_out_file[CFSOF_col_flow].iloc[0]].sum(
        )

        # Initial(ised) data columns
    # MIKEL: por el momento, los siguientes dos datos no los gestionamos en forma de parámetros porque no conseguimos sacarlos.
    #     df_results_acuifero[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]] = dic_acuiferos[acuifero].max_flow # (Initial) max flow

        # SOLUCION: utilizamos los df de parámetros creados en la fase de inicio:
        # Serie de valores de recarga de acuífero definidos como parámetro al inicio
        if (p_simulation_step == SIMULATION_STEP_PASO_MENSUAL):
            # Serie de valores de recarga de acuífero
            df_all_values_element = df_PARAMS_ACUIFEROS_recarga_mensual[[
                dic_acuiferos[acuifero].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_month_of_year-1):simul_end_month_of_year, :]
        else:  # (p_simulation_step == SIMULATION_STEP_PASO_DIARIO):
            # Serie de valores de recarga de acuífero
            df_all_values_element = df_PARAMS_ACUIFEROS_recarga_diario[[
                dic_acuiferos[acuifero].comment]]
            df_list_values_simulation = df_all_values_element.iloc[(
                simul_start_day_of_year-1):simul_end_day_of_year, :]

        # Asignamos los valores
        df_results_acuifero[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]
                            ] = df_list_values_simulation.values

        # Seguimos con otros calculos
        df_results_acuifero[df_config_out_file[CFSOF_col_flow_supplied_rate].iloc[0]] = \
            df_results_acuifero[df_config_out_file[CFSOF_col_flow].iloc[0]] / \
            df_results_acuifero[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]]

        df_results_acuifero[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]] = \
            df_results_acuifero[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
        )
        df_results_acuifero[df_config_out_file[CFSOF_col_total_flow_supplied_rate].iloc[0]] = \
            df_results_acuifero[df_config_out_file[CFSOF_col_total_flow].iloc[0]] / \
            df_results_acuifero[df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0]]

        # Continuamos con un valor que no viene de un parámetro de tipo serie
        df_results_acuifero[df_config_out_file[CFSOF_col_cost].iloc[0]
                            ] = dic_acuiferos[acuifero].cost  # (Initial) cost

        # Actualizar el df con la info de todos los acuiferos
        if (acuifero == primer_nodo):
            df_results_acuiferos = df_results_acuifero.copy()
        else:
            df_results_acuiferos = pd.concat(
                [df_results_acuiferos, df_results_acuifero.copy()], ignore_index=True)

    # Calcular datos agregados totales
    df_results_acuiferos[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_real].iloc[0]] = \
        df_results_acuiferos[df_config_out_file[CFSOF_col_flow].iloc[0]].sum()
    g_col_total_flow_acuiferos_all_real = \
        df_results_acuiferos[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_real].iloc[0]].values[0]

    df_results_acuiferos[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_prev].iloc[0]] = \
        df_results_acuiferos[df_config_out_file[CFSOF_col_init_max_flow].iloc[0]].sum(
    )
    g_col_total_flow_acuiferos_all_prev = \
        df_results_acuiferos[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_prev].iloc[0]].values[0]

    df_results_acuiferos[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_supplied_rate].iloc[0]] = \
        g_col_total_flow_acuiferos_all_real / g_col_total_flow_acuiferos_all_prev
    g_col_total_flow_acuiferos_all_supplied_rate = \
        df_results_acuiferos[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_supplied_rate].iloc[0]].values[0]

    # Reorder columns
    # columnas = df_results_acuiferos.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_cost].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_flow_supplied_rate].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_init_max_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_supplied_rate].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_acuiferos_all_real].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_acuiferos_all_prev].iloc[0],
                df_config_out_file[CFSOF_col_total_flow_acuiferos_all_supplied_rate].iloc[0]]

    df_results_acuiferos = df_results_acuiferos[columnas]
    df_results_acuiferos.reset_index(drop=True, inplace=True)

    '''
    Calcular + guardar datos de RECORDERS de (10) RETORNO_GLOBAL <---> Output
    '''

    # Guardar datos en dataframe (ID, nombre (descripción), timestamp y recorders data)
    df_results_retorno_global = recorder_retorno_global_flow.to_dataframe()
    df_results_retorno_global.columns = [
        df_config_out_file[CFSOF_col_flow].iloc[0]]
    df_results_retorno_global[df_config_out_file[CFSOF_col_mean_flow].iloc[0]] = \
        df_results_retorno_global[df_config_out_file[CFSOF_col_flow].iloc[0]].mean(
    )
    df_results_retorno_global[df_config_out_file[CFSOF_col_total_flow].iloc[0]] = \
        df_results_retorno_global[df_config_out_file[CFSOF_col_flow].iloc[0]].sum(
    )
    df_results_retorno_global[df_config_out_file[CFSOF_col_id].iloc[0]
                              ] = g_retorno_global.name  # Node ID
    df_results_retorno_global[df_config_out_file[CFSOF_col_name].iloc[0]
                              ] = g_retorno_global.comment  # Node name (description)
    df_results_retorno_global[df_config_out_file[CFSOF_col_timestamp].iloc[0]
                              ] = df_results_retorno_global.index  # Timestamp

    # Reorder columns
    # columnas = df_results_retorno_global.columns
    # columnas_temp = list(set(columnas) - set([df_config_out_file[CFSOF_col_timestamp].iloc[0], \
    #                                           df_config_out_file[CFSOF_col_id].iloc[0], df_config_out_file[CFSOF_col_name].iloc[0]]))
    # columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0], df_config_out_file[CFSOF_col_id].iloc[0], \
    #             df_config_out_file[CFSOF_col_name].iloc[0]] + columnas_temp

    columnas = [df_config_out_file[CFSOF_col_timestamp].iloc[0],
                df_config_out_file[CFSOF_col_id].iloc[0],
                df_config_out_file[CFSOF_col_name].iloc[0],
                df_config_out_file[CFSOF_col_flow].iloc[0],
                df_config_out_file[CFSOF_col_mean_flow].iloc[0],
                df_config_out_file[CFSOF_col_total_flow].iloc[0]]

    df_results_retorno_global = df_results_retorno_global[columnas]
    df_results_retorno_global.reset_index(drop=True, inplace=True)

    # Imprimir datos TOTALES

    # Crate an emtpy dataframe first
    df_totales = pd.DataFrame()

    # Calculate g_col_total_flow_INPUT_all_prev
    g_col_total_flow_INPUT_all_prev = g_col_total_flow_aportaciones_all_prev + \
        g_col_total_flow_retornos_input_all_prev + g_col_total_flow_acuiferos_all_prev

    # Calculate g_col_total_flow_INPUT_all_real
    g_col_total_flow_INPUT_all_real = g_col_total_flow_aportaciones_all_real + g_col_total_flow_retornos_input_all_real + \
        g_col_total_flow_acuiferos_all_real
    # Security check
    if (abs(g_col_total_flow_INPUT_all_prev) == np.inf):
        g_col_total_flow_INPUT_all_prev = g_col_total_flow_INPUT_all_real

    # Calculate g_col_total_flow_OUTPUT_all_prev
    g_col_total_flow_OUTPUT_all_prev = g_col_total_flow_demandas_all_prev + \
        g_col_total_flow_retornos_output_all_prev

    # Calculate g_col_total_flow_OUTPUT_all_real
    g_col_total_flow_OUTPUT_all_real = g_col_total_flow_demandas_all_real + \
        g_col_total_flow_retornos_output_all_real

    # Security check
    if (abs(g_col_total_flow_OUTPUT_all_prev) == np.inf):
        g_col_total_flow_OUTPUT_all_prev = g_col_total_flow_OUTPUT_all_real

    # Save values
    # Aportaciones: previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_aportaciones_all_prev) == np.inf):
        g_col_total_flow_aportaciones_all_prev = g_col_total_flow_aportaciones_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_prev].iloc[0]] = \
        [g_col_total_flow_aportaciones_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_real].iloc[0]] = \
        [g_col_total_flow_aportaciones_all_real]
    df_totales[df_config_out_file[CFSOF_col_total_flow_aportaciones_all_supplied_rate].iloc[0]] = \
        [g_col_total_flow_aportaciones_all_supplied_rate]

    # Retornos (input): previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_retornos_input_all_prev) == np.inf):
        g_col_total_flow_retornos_input_all_prev = g_col_total_flow_retornos_input_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_prev].iloc[0]] = \
        [g_col_total_flow_retornos_input_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_real].iloc[0]] = \
        [g_col_total_flow_retornos_input_all_real]
    df_totales[df_config_out_file[CFSOF_col_total_flow_retornos_input_all_supplied_rate].iloc[0]] = \
        [g_col_total_flow_retornos_input_all_supplied_rate]

    # Retornos (output): previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_retornos_output_all_prev) == np.inf):
        g_col_total_flow_retornos_output_all_prev = g_col_total_flow_retornos_output_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_prev].iloc[0]] = \
        [g_col_total_flow_retornos_output_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_real].iloc[0]] = \
        [g_col_total_flow_retornos_output_all_real]
    df_totales[df_config_out_file[CFSOF_col_total_flow_retornos_output_all_deficit_percent].iloc[0]] = \
        [g_col_total_flow_retornos_output_all_deficit_percent]

    # Acuiferos: previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_acuiferos_all_prev) == np.inf):
        g_col_total_flow_acuiferos_all_prev = g_col_total_flow_acuiferos_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_prev].iloc[0]] = \
        [g_col_total_flow_acuiferos_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_real].iloc[0]] = \
        [g_col_total_flow_acuiferos_all_real]
    df_totales[df_config_out_file[CFSOF_col_total_flow_acuiferos_all_supplied_rate].iloc[0]] = \
        [g_col_total_flow_acuiferos_all_supplied_rate]

    # Input TOTAL: previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_INPUT_all_prev) == np.inf):
        g_col_total_flow_INPUT_all_prev = g_col_total_flow_INPUT_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_INPUT_all_prev].iloc[0]] = [
        g_col_total_flow_INPUT_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_INPUT_all_real].iloc[0]] = [
        g_col_total_flow_INPUT_all_real]
    try:
        df_totales[df_config_out_file[CFSOF_col_total_flow_INPUT_all_supplied_rate].iloc[0]] = \
            g_col_total_flow_INPUT_all_real / g_col_total_flow_INPUT_all_prev
    except:
        df_totales[df_config_out_file[CFSOF_col_total_flow_INPUT_all_supplied_rate].iloc[0]] = 100

    # Demanda TOTAL: previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_demandas_all_prev) == np.inf):
        g_col_total_flow_demandas_all_prev = g_col_total_flow_demandas_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_demandas_all_prev].iloc[0]] = [
        g_col_total_flow_demandas_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_demandas_all_real].iloc[0]] = [
        g_col_total_flow_demandas_all_real]
    df_totales[df_config_out_file[CFSOF_col_total_flow_demandas_all_deficit_percent].iloc[0]] = \
        [g_col_total_flow_demandas_all_deficit_percent]

    # Output TOTAL: previsto, real, déficit (%)
    # Security check
    if (abs(g_col_total_flow_OUTPUT_all_prev) == np.inf):
        g_col_total_flow_OUTPUT_all_prev = g_col_total_flow_OUTPUT_all_real

    # Now, go ahead
    df_totales[df_config_out_file[CFSOF_col_total_flow_OUTPUT_all_prev].iloc[0]] = [
        g_col_total_flow_OUTPUT_all_prev]
    df_totales[df_config_out_file[CFSOF_col_total_flow_OUTPUT_all_real].iloc[0]] = [
        g_col_total_flow_OUTPUT_all_real]
    try:
        df_totales[df_config_out_file[CFSOF_col_total_flow_demandas_all_deficit_percent].iloc[0]] = \
            [(g_col_total_flow_OUTPUT_all_prev - g_col_total_flow_OUTPUT_all_real) /
             g_col_total_flow_OUTPUT_all_prev * 100]
    except:
        df_totales[df_config_out_file[CFSOF_col_total_flow_demandas_all_deficit_percent].iloc[0]] = 100

    '''
    ---------------------------------------------------------------------
    ---------------------------------------------------------------------
    '''

    # GUARDAR LOS RESULTADOS

    # Primero, generar el reparto del agua por tipo de agua de manera aleartoria
    # La distribución del tipo de agua la generaremos de forma aleatoria.
    for demanda in dic_demandas:

        # 1. Primero, generar 5 números reales aleatorios:
        random_numbers = np.random.random(5)

        # 2. Segundo,escalarlo a 1:
        random_numbers_scaled = random_numbers / random_numbers.sum()

        # 3. Asignar los números aleatorios escalados al reparto
        df_results_demandas.loc[df_results_demandas['id'] == demanda,
                                'tipo_agua_superficial'] = random_numbers_scaled[0]
        df_results_demandas.loc[df_results_demandas['id'] == demanda,
                                'tipo_agua_subterranea'] = random_numbers_scaled[1]
        df_results_demandas.loc[df_results_demandas['id'] == demanda,
                                'tipo_agua_reutilizada'] = random_numbers_scaled[2]
        df_results_demandas.loc[df_results_demandas['id'] ==
                                demanda, 'tipo_agua_trasvase'] = random_numbers_scaled[3]
        df_results_demandas.loc[df_results_demandas['id'] ==
                                demanda, 'tipo_agua_desalada'] = random_numbers_scaled[4]
        df_results_demandas.loc[df_results_demandas['id'] == demanda, 'impacto_co2'] = \
            np.random.uniform(low=-353.7, high=564.1, size=1)[0]
        df_results_demandas.loc[df_results_demandas['id'] == demanda, 'impacto_hidroeconomico'] = \
            np.random.uniform(low=-753.7, high=1004.5, size=1)[0]

    # Primero, de df_results_demandas, tomas los campos que nos interesan:
    df_results_for_L4_L5 = df_results_demandas[['timestamp', 'id', 'name', 'flow', 'init_max_flow', 'total_flow',
                                                g_col_demanda_tipo, g_col_demanda_tipo_nombre, g_col_demanda_mi_id,
                                                'tipo_agua_superficial', 'tipo_agua_subterranea', 'tipo_agua_reutilizada',
                                                'tipo_agua_trasvase', 'tipo_agua_desalada',
                                                'impacto_co2', 'impacto_hidroeconomico']].copy()
    return df_results_for_L4_L5

