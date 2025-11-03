import { Geometry } from "geojson";
import { MapMouseEvent, MapboxGeoJSONFeature, EventData } from "mapbox-gl";

interface ResponseData {
    ok: boolean;
    status: number;
}

export interface ResponseDataStringArray extends ResponseData {
    data: string[];
}

export interface Layer {
    title: string;
    layer: string;
}

export interface ResponseDataLayer extends ResponseData {
    data: Layer[];
}

export interface Style {
    title: string;
    style: string;
}

export interface RespondeDataStyles extends ResponseData {
    data: {
        layer: string;
        styles: Style[];
    };
}

export interface ResponseLayerDates extends ResponseData {
    data: Array<string>;
}

export interface ResponseError extends ResponseData {
    title: string;
    detail: string;
}

export interface ResponseDownloadData extends ResponseData {
    data: Blob;
}

interface BaseFilterFormInterface {
    valid: boolean;
}

export interface BasicFormInterface extends BaseFilterFormInterface {
    variable: string;
    timeRange: string;
    customTimeRange: string[];
    predictionEnabled?: boolean;
    forecasting?: number;
    simulationEnabled?: boolean;
    simulation?: number;
}

export type FormActions = Vue & {
    validate: () => boolean;
    resetValidation: () => boolean;
    reset: () => void;
};

export type FormBtnAction = Partial<{
    variable: string;
    startDate: Date;
    endDate: Date;
    forecasting: number;
    simulation: number;
}>;

export interface CPPiezometerForm extends BaseFilterFormInterface {
    timeRange: string;
    layerPzmtrs: boolean;
    layerAqfrs: boolean;
}

export interface WaterMeterForm extends BaseFilterFormInterface {
    layerAqfrs: boolean;
    layerUndrgrnd: boolean;
    layerWM: boolean;
}

/**
 * User
 */
export interface UserRole {
    text: string;
    value: string;
}

export interface UserData {
    name: string;
}

/**
 * Predictions
 */

export interface PredictionLayer {
    layer: string;
    title: string;
}

export interface PredictionStyle {
    style: string;
    title: string;
}

export interface WMSSliderFormInterface {
    date: string;
    dateText: string;
    value: number;
    step: number;
    max: number;
    disabled: boolean;
}

export interface WMSFilterFormInterface extends BaseFilterFormInterface {
    layer: PredictionLayer;
    style: PredictionStyle;
    selectedDate: string;
    line: number;
}

export interface DemandUnitRasterStats {
    mean: number;
    sum: number;
}
export interface DemandUnitRasterStatsResponse extends ResponseData {
    data: {
        values: DemandUnitRasterStats[];
        bins: number[];
    };
}

/**
 * Scenario analysis
 */
export interface ScenarioAnalysisFormInterface extends BaseFilterFormInterface {
    subterranea: number;
    superficial: number;
    reutilizada: number;
    desalada: number;
    trasvase: number;
    waterDeficit: number;
    CO2impact: number;
    economicImpact: number;
}

export interface ScenarioAnalysisExecutionResponse extends ResponseData {
    data: string;
}

/**
 * Planer
 */
export interface PlannerPlotData {
    date: string[];
    demand: number[];
    planned: number[];
    incertLow: number[];
    incertHigh: number[];
    superficial: number[];
    subterranea: number[];
    reutilizada: number[];
    trasvase: number[];
    desalada: number[];
    CO2: number[];
    economic: number[];
}

export interface PlannerAvailableResources {
    subterranea: number;
    superficial: number;
    reutilizada: number;
    desalada: number;
    trasvase: number;
}

export interface PlannerAvailableResourcesResponse extends ResponseData {
    data: PlannerAvailableResources[];
}

export interface PlannerDemandResources {
    AMBIENTAL: number;
    UDA: number;
    UDU: number;
    UDI: number;
    UDRG: number;
}

export interface PlannerDemandResourcesResponse extends ResponseData {
    data: {
        availableResources: PlannerAvailableResources;
        demandResources: PlannerDemandResources;
    };
}

export interface PlannerPlotDataResponse extends ResponseData {
    data: PlannerPlotData;
}

export interface PlannerTableData {
    name: string;
    route: string | undefined;
    demand: number;
    planned: number;
    dates: string[];
    deficit: number;
    deficitPerDay: number[];
    superficial: number[];
    subterranea: number[];
    reutilizada: number[];
    trasvase: number[];
    desalada: number[];
    emission: number[];
    economic: number[];
}

export interface PlannerConfigData {
    CO2impact: number;
    waterDeficit: number;
    economicImpact: number;
    superficial: number;
    subterranea: number;
    reutilizada: number;
    trasvase: number;
    desalada: number;
    start: string;
    end: string;
    creationDate: string;
}

export interface PlannerTableDataResponse extends ResponseData {
    data: PlannerTableData[];
}

export interface PlannerConfigDataResponse extends ResponseData {
    data: PlannerConfigData;
}

/**
 * Optimizer
 */
export interface OptimizerPlotData extends PlannerPlotData {
    oldPlan?: PlannerPlotData;
}

export interface OptimizerPlotDataResponse extends ResponseData {
    data: OptimizerPlotData;
}

/**
 * Environmental flow
 */
export interface EnvironmentalFlowResponse extends ResponseData {
    data: EnvironmentalFlow[];
}

export interface EnvironmentalFlow {
    typology: string;
    variable: string;
    water_body: WaterBody;
    masa_estrategica: boolean;
    sistema: number;
    ene_mar: number;
    abr_jun: number;
    jul_sep: number;
    oct_dic: number;
    ene_mar_seq: number | null;
    abr_jun_seq: number | null;
    jul_sep_seq: number | null;
    oct_dic_seq: number | null;
}

export interface EnvironmentalFlowDrought extends EnvironmentalFlow {
    inDrought?: boolean;
}

export interface WaterBody {
    code: string;
    geometry: Geometry;
    name: string;
    generator_flow: number | null;
    type?: string;
}

export interface WaterBodyResponse extends ResponseData {
    data: WaterBody[];
}

/**
 * Dams
 */
export interface Dam {
    variable: string;
    typology: string;
    water_body: WaterBody;
    max_oct_dic: number;
    max_ene_mar: number;
    max_abr_jun: number;
    max_jul_sep: number;
    min_oct_dic: number;
    min_ene_mar: number;
    min_abr_jun: number;
    min_jul_sep: number;
}

export interface DamResponse extends ResponseData {
    data: Dam[];
}

export interface DamVariable {
    variable: string;
    typology: string;
}

export interface DamVariableResponse extends ResponseData {
    data: DamVariable[];
}

/**
 * CO2
 */
export interface CO2FilterFormInterface extends BaseFilterFormInterface {
    layer: string;
    period: string;
}

/**
 * Hydro-economic
 */
export interface HydroEconomic {
    income: number;
    demanda_mi_id: string;
}

export interface HydroEconomicResponse extends ResponseData {
    data: HydroEconomic[];
}

export interface HydroEconomicFilterFormInterface
    extends BaseFilterFormInterface {
    layer: string;
    period: string;
}

/**
 * DemandUnits
 */
export interface DemandUnit {
    code: string;
    type: string;
    geometry: Geometry;
    name: string;
}

export interface DemandUnitResponse extends ResponseData {
    data: DemandUnit[];
}

export interface WaterEmission {
    desalada: number;
    reutilizada: number;
    subterranea: number;
    superficial: number;
    trasvase: number;
    total: number;
}

export interface DemandUnitEmission {
    code: string;
    total: number;
    demand: number;
    water: WaterEmission;
}

export interface DemandUnitEmissionsResponse extends ResponseData {
    data: {
        emissions: DemandUnitEmission[];
        bins: number[];
    };
}

export interface DemandUnitIncome {
    income: number;
    code: string;
}

export interface DemandUnitIncomeResponse extends ResponseData {
    data: {
        hydroEconomic: DemandUnitIncome[];
        bins: number[];
    };
}

export interface DemandUnitFormInterface extends BaseFilterFormInterface {
    agriculture: boolean;
    urban: boolean;
    industry: boolean;
    golf: boolean;
    wetland: boolean;
}

/**
 * Variable values
 */
export interface VariableValueResponse extends ResponseData {
    data: VariableValue[];
}

export interface VariableValue {
    _time: number;
    _value: number;
    variableCode: string;
}

export type TypedVariableValue = VariableValue & {
    type?: "real" | "predicted" | "simulated";
};

/**
 * Variables
 */
export interface VariableResponse extends ResponseData {
    data: Variable[];
}

export interface Variable {
    code: string;
    description: string;
    measurement_point: MeasurementPoint;
    typology: string;
}

/**
 * Measurement points
 */
export interface MeasurementPoint {
    code: string;
    denomination: string;
    typology: string;
    description: string;
    location: Geometry;
    variables: Variable[];
}

export interface MeasurementPointResponse extends ResponseData {
    data: MeasurementPoint[];
}

/**
 * UI
 */
export interface ComboBoxItem {
    text: string | number | object;
    value: string | number | object;
    disabled?: boolean;
    divider?: boolean;
    header?: string;
}

export type LegendItem = {
    color: string;
    text: string;
};

export interface WMSStatsResponse extends ResponseData {
    data: string;
}

export type MBMouseEvent = MapMouseEvent & {
    features?: MapboxGeoJSONFeature[] | undefined;
} & EventData;

/**
 * Corporate Piezometry
 */
export interface CPPiezometer {
    COD_CHS: string;
    location: Geometry;
    Z: number;
    ACUIFERO: string;
    MSBT_Nombre: string;
    COD_MASA_DEM: string;
    CodMasa: string;
}

export interface CPPiezometerResponse extends ResponseData {
    data: CPPiezometer[];
}

export interface CPAquifer {
    id: string;
    name: string;
    mstb: string; // Masa SuBTerránea
    piezometerIds: string[];
    geometry?: Geometry;
}

/**
 * Prediccions
 */
export interface ForecastValue {
    ds: number;
    yhat: number;
    yhat_lower: number;
    yhat_upper: number;
}

export interface ForecastResponse extends ResponseData {
    data: ForecastValue[];
}

/**
 * Simulation
 */
export interface SimulationResponse extends ResponseData {
    data: VariableValue[];
}

/**
 * Water Meter
 */

export interface WaterMeter {
    CodigoPVYCR: string;
    idElementoMedida: string | null;
    DenominacionPunto: string | null;
    Funciona: string | null;
    Fecha_Medida: string | null;
    location: Geometry;
    INSCRIPCION: string | null;
    OtrosExpedientes: string | null;
    NombreTitular: string | null;
    VolumenMaximoAnualLegal_M3: number | null;
    MunicipioToma: string | null;
    DenominacionCauce: string | null;
}

export interface WaterMeterResponse extends ResponseData {
    data: WaterMeter[];
}

/**
 * Drought indices
 */
export interface DroughtIndices {
    FECHA: string;
    CUENCA: number;
    TRASVASE: number;
    GLOBAL: number;
    UTE_I_Situacion: string;
    UTE_I_Escenario: string;
    UTE_II_Cabecera: number;
    UTE_II_Situacion: string;
    UTE_II_Escenario: string;
    UTE_III_RiosMI: number;
    UTE_III_Situacion: string;
    UTE_III_Escenario: string;
    UTE_IV_RiosMD: number;
    UTE_IV_Situacion: string;
    UTE_IV_Escenario: string;
    UTS_I_Principal: number;
    UTS_I_Principal_Situacion: string;
    UTS_II_Cabecera_Situacion: string;
    UTS_III_RiosMI_Situacion: string;
    UTS_IV_RiosMD_Situacion: string;
    UTS_GlobalSegura: number;
    UTS_Global_Segura_Situacion: string;
    Alto_Tajo: number;
    Alto_Tajo_Situacion: string;
}

export interface DroughtIndicesResponse extends ResponseData {
    data: DroughtIndices[];
}

/**
 * System units
 */
export interface SystemUnits {
    zone: string;
    geometry: Geometry;
    name: string;
    ha: number;
}

export interface SystemUnitsResponse extends ResponseData {
    data: SystemUnits[];
}

/**
 * Login interfaces
 */
export interface LoginVerificationResponse extends ResponseData {
    data: {
        username: string;
    };
}

export interface LogoutResponse extends ResponseData {
    data: {
        cas_logout_url: string | null;
    };
}
