import _Vue from "vue";
import axios, { AxiosError, AxiosResponse } from "axios";

import { ResponseError } from "@/interfaces";

const client = axios.create({
    baseURL: process.env.VUE_APP_API_URL || window.location.origin + "/api"
});

export class APIService {
    async execute<T>(
        method: "get" | "post" | "put" | "delete",
        resource: string,
        data: unknown = null
    ) {
        return client
            .request<T>({
                method,
                url: resource,
                data
            })
            .then((res: AxiosResponse) => {
                return res.data;
            })
            .catch((e: AxiosError) => {
                console.error(e);
                console.log(e.response?.data);

                const errorData: ResponseError | string = e.response?.data;

                /**
                 * Sometimes errorData is an string. Ex: "Unauthorized Access"
                 */
                if (typeof errorData === "string") {
                    const txt = errorData;
                    throw new Error(txt);
                }

                const txt = errorData ? errorData.detail : e.message;
                throw new Error(txt);
            }) as Promise<T>;
    }

    async executeDownload<T>(
        method: "get" | "post" | "put" | "delete",
        resource: string,
        data: unknown = null
    ) {
        return client
            .request<T>({
                method,
                url: resource,
                data,
                responseType: "blob"
            })
            .then((res: AxiosResponse) => {
                return res;
            })
            .catch((e: AxiosError) => {
                console.error(e);
                console.log(e.response?.data);

                const errorData: ResponseError | string = e.response?.data;

                /**
                 * Sometimes errorData is an string. Ex: "Unauthorized Access"
                 */
                if (typeof errorData === "string") {
                    const txt = errorData;
                    throw new Error(txt);
                }

                const txt = errorData ? errorData.detail : e.message;
                throw new Error(txt);
            });
    }

    getEnvironmentalFlowWaterBodies<T>(): Promise<T> {
        return this.execute<T>("get", "/environmental-flow/get-water-bodies");
    }

    getDamsVariables<T>(): Promise<T> {
        return this.execute<T>("get", "/dam/get-dams-variables");
    }

    getDamVariables<T>(dam: string): Promise<T> {
        return this.execute<T>("get", `/dam/get-dam-variables?dam=${dam}`);
    }

    getDamByVariable<T>(variable: string): Promise<T> {
        return this.execute<T>(
            "get",
            `/dam/get-dam-by-variable?variable=${variable}`
        );
    }

    getDamsVariableTypology<T>(typology: string): Promise<T> {
        return this.execute<T>(
            "get",
            `/dam/get-dams-variable-typology?typology=${typology}`
        );
    }

    getVariables<T>(variables: string[]): Promise<T> {
        return this.execute<T>("post", "/saih/get-variables", {
            variables
        });
    }

    getVariablesLastValues<T>(variables: string[]): Promise<T> {
        return this.execute<T>("post", "/saih/get-variable-last-values", {
            variables
        });
    }

    getLayers<T>(line) {
        if (line) {
            return this.execute<T>(
                "get",
                `/predictions/get-layers?line=${line}`
            );
        } else {
            return this.execute<T>("get", "/predictions/get-layers");
        }
    }

    getStyles<T>(layer) {
        if (layer) {
            return this.execute<T>(
                "get",
                `/predictions/get-styles?layer=${layer}`
            );
        } else {
            return this.execute<T>("get", "/predictions/get-styles");
        }
    }

    getDates<T>(layer) {
        return this.execute<T>("get", `/predictions/get-dates?layer=${layer}`);
    }

    getVariablesValues<T>(
        variables: string[],
        startDate: Date,
        endDate: Date,
        aggregation: string | undefined = undefined,
        window: string | undefined = undefined
    ): Promise<T> {
        let body: {
            variables: string[];
            start_date: string;
            end_date: string;
            aggregation?: string;
            window?: string;
        } = {
            variables,
            ["start_date"]: startDate.toISOString(),
            ["end_date"]: endDate.toISOString()
        };

        if (aggregation && window) {
            body = {
                ...body,
                aggregation,
                window
            };
        }

        return this.execute<T>("post", "/saih/get-variable-values", body);
    }

    getPiezometers<T>() {
        return this.execute<T>("get", "/saih/get-piezometers");
    }

    getCPPiezometers<T>() {
        return this.execute<T>("post", "/corporate/get-piezometers");
    }

    getCPPiezometersValues<T>(codes: string[], config) {
        const body = {
            variables: codes,
            ...config
        };

        return this.execute<T>(
            "post",
            "/corporate/get-piezometers-values",
            body
        );
    }

    getWMSGeometryStats<T>(
        layer: string,
        style: string,
        startDate: string,
        endDate: string,
        geometry
    ): Promise<T> {
        return this.execute<T>("post", "/predictions/get-wms-stats", {
            product: layer,
            measurement: style,
            "start-date": startDate,
            "end-date": endDate,
            geometry: geometry
        });
    }

    getDemandUnitRasterStats<T>(date: string, product: string): Promise<T> {
        return this.execute<T>(
            "get",
            `/predictions/get-uda-stats?date=${date}&product=${product}`
        );
    }

    downloadDemandUnitRasterStats<T>(date: string, product: string) {
        return this.executeDownload<T>(
            "get",
            `/predictions/download-uda-stats?date=${date}&product=${product}`
        );
    }

    downloadRaster<T>(date: string, product: string) {
        return this.executeDownload<T>(
            "get",
            `/predictions/download-raster-file?date=${date}&product=${product}`
        );
    }

    downloadPlannerData<T>(length: boolean, daily: boolean) {
        return this.executeDownload<T>(
            "get",
            `/line4/download-plan?long=${length}&daily=${daily}`
        );
    }

    downloadOptimizerData<T>(length: boolean, daily: boolean) {
        return this.executeDownload<T>(
            "get",
            `/line5/download-plan?length=${length}&daily=${daily}`
        );
    }

    getDatabaseGeometryStats<T>(
        layer: string,
        startDate: string,
        endDate: string,
        geometry
    ): Promise<T> {
        return this.execute<T>("post", "/predictions/get-database-stats", {
            layer: layer,
            start: startDate,
            end: endDate,
            geometry: geometry
        });
    }

    getWaterBodies<T>({ code, type }: { code?: string; type?: string } = {}) {
        const url = "/water-body/get-values";

        const params = new URL("https://www.localhost.dev/");
        if (code) params.searchParams.append("code", code);
        if (type) params.searchParams.append("type", type);

        return this.execute<T>("get", url + params.search);
    }

    getDemandUnits<T>(
        type: string | undefined = undefined,
        code: string | undefined = undefined
    ) {
        if (type && code) {
            return this.execute<T>(
                "get",
                `/demand-unit/get-values?type=${type}&code=${code}`
            );
        } else if (type && !code) {
            return this.execute<T>(
                "get",
                `/demand-unit/get-values?type=${type}`
            );
        } else if (!type && code) {
            return this.execute<T>(
                "get",
                `/demand-unit/get-values?code=${code}`
            );
        } else {
            return this.execute<T>("get", "/demand-unit/get-values");
        }
    }

    getAgricultureEmissions<T>(period: string, line: string) {
        return this.execute<T>(
            "get",
            `/co2/get-agriculture-emissions?period=${period}&line=${line}`
        );
    }

    getUrbanEmissions<T>(period: string, line: string) {
        return this.execute<T>(
            "get",
            `/co2/get-urban-emissions?period=${period}&line=${line}`
        );
    }

    getIndustrialEmissions<T>(period: string, line: string) {
        return this.execute<T>(
            "get",
            `/co2/get-industry-emissions?period=${period}&line=${line}`
        );
    }

    getGolfEmissions<T>(period: string, line: string) {
        return this.execute<T>(
            "get",
            `/co2/get-golf-emissions?period=${period}&line=${line}`
        );
    }

    getWetlandEmissions<T>(period: string, line: string) {
        return this.execute<T>(
            "get",
            `/co2/get-wetland-emissions?period=${period}&line=${line}`
        );
    }

    getAgricultureIncome<T>(line: string, period: string) {
        return this.execute<T>(
            "get",
            `/hydro-economic/get-agriculture-income?line=${line}&period=${period}`
        );
    }

    getUrbanIncome<T>(line: string, period: string) {
        return this.execute<T>(
            "get",
            `/hydro-economic/get-urban-income?line=${line}&period=${period}`
        );
    }

    getIndustrialIncome<T>(line: string, period: string) {
        return this.execute<T>(
            "get",
            `/hydro-economic/get-industry-income?line=${line}&period=${period}`
        );
    }

    getGolfIncome<T>(line: string, period: string) {
        return this.execute<T>(
            "get",
            `/hydro-economic/get-golf-income?line=${line}&period=${period}`
        );
    }

    getWetlandIncome<T>(line: string, period: string) {
        return this.execute<T>(
            "get",
            `/hydro-economic/get-wetland-income?line=${line}&period=${period}`
        );
    }

    getForecast<T>(
        variable: string,
        forecasting = 1,
        db: "odc" | "corp" = "odc",
        aggregation = "mean"
    ) {
        return this.execute<T>(
            "get",
            `/predictions/variable-prediction?variable=${variable}&forecasting=${forecasting}&aggregation=${aggregation}&database=${db}`
        );
    }

    getSimulation<T>(
        variables: string[],
        startDate: Date,
        endDate: Date,
        simulation = 0,
        aggregation: string | undefined = undefined,
        window: string | undefined = undefined
    ) {
        let body: {
            variables: string[];
            start_date: string;
            end_date: string;
            simulation_range?: number;
            aggregation?: string;
            window?: string;
        } = {
            variables,
            ["start_date"]: startDate.toISOString(),
            ["end_date"]: endDate.toISOString()
        };

        if (simulation) {
            body = {
                ...body,
                ["simulation_range"]: simulation
            };
        }

        if (aggregation && window) {
            body = {
                ...body,
                aggregation,
                window
            };
        }

        return this.execute<T>("post", "/line2/simulation/get-values", body);
    }

    generatePlan<T>(
        monthly: boolean,
        daily: boolean,
        scenario,
        optimized: boolean
    ) {
        if (optimized) {
            return this.execute<T>(
                "post",
                `/line5/generate-optimized-plan?monthly=${monthly}&daily=${daily}`,
                { scenario }
            );
        } else {
            return this.execute<T>(
                "post",
                `/line4/generate-plan?monthly=${monthly}&daily=${daily}`,
                { scenario }
            );
        }
    }

    checkPlanGenerated<T>(id: string) {
        return this.execute<T>("get", `/line4/check-plan-generated?id=${id}`);
    }

    getAvailableResources<T>() {
        return this.execute<T>("get", "/line4/get-resources");
    }

    getDemandResources<T>() {
        return this.execute<T>("get", "/line4/get-demand-resources");
    }

    getPlannerPlotData<T>(category, ud, monthly, daily) {
        if (ud) {
            return this.execute<T>(
                "get",
                `/line4/plot-data?id=${ud}&monthly=${monthly}&daily=${daily}`
            );
        } else if (category) {
            return this.execute<T>(
                "get",
                `/line4/plot-data?type=${category}&monthly=${monthly}&daily=${daily}`
            );
        } else {
            return this.execute<T>(
                "get",
                `/line4/plot-data?monthly=${monthly}&daily=${daily}`
            );
        }
    }

    getOptimizerPlotData<T>(category, ud, monthly, daily) {
        if (ud) {
            return this.execute<T>(
                "get",
                `/line5/plot-data?id=${ud}&monthly=${monthly}&daily=${daily}`
            );
        } else if (category) {
            return this.execute<T>(
                "get",
                `/line5/plot-data?type=${category}&monthly=${monthly}&daily=${daily}`
            );
        } else {
            return this.execute<T>(
                "get",
                `/line5/plot-data?monthly=${monthly}&daily=${daily}`
            );
        }
    }

    getPlannerTableData<T>(category, monthly, daily) {
        if (category) {
            return this.execute<T>(
                "get",
                `/line4/table-data?type=${category}&monthly=${monthly}&daily=${daily}`
            );
        } else {
            return this.execute<T>(
                "get",
                `/line4/table-data?monthly=${monthly}&daily=${daily}`
            );
        }
    }

    getPlanConfigData<T>(monthly, daily) {
        return this.execute<T>(
            "get",
            `/line4/plan-config-data?monthly=${monthly}&daily=${daily}`
        );
    }

    getOptimizedPlanConfigData<T>(monthly, daily) {
        return this.execute<T>(
            "get",
            `/line5/optimized-plan-config-data?monthly=${monthly}&daily=${daily}`
        );
    }

    checkOptimizedPlanGenerated<T>(id: string) {
        return this.execute<T>(
            "get",
            `/line5/check-optimized-plan-generated?id=${id}`
        );
    }

    getOptimizerTableData<T>(category, monthly, daily) {
        if (category) {
            return this.execute<T>(
                "get",
                `/line5/table-data?type=${category}&monthly=${monthly}&daily=${daily}`
            );
        } else {
            return this.execute<T>(
                "get",
                `/line5/table-data?monthly=${monthly}`
            );
        }
    }

    getMeasurementPoints<T>(
        params: { variables?: string[]; typology?: string[] } = {}
    ) {
        return this.execute<T>("post", "/saih/get-measurement-points", {
            ...params
        });
    }

    getSaicaForecast<T>(station: string, target: string, forecasting = 1) {
        return this.execute<T>("post", `/saica/prediction`, {
            station,
            target,
            forecasting
        });
    }

    getWaterMeters<T>(): Promise<T> {
        return this.execute<T>("get", `/water-meters`);
    }

    getWaterMetersValues<T>(
        variableValue: string,
        startDate: Date,
        endDate: Date
    ): Promise<T> {
        const body = {
            ["start_date"]: startDate.toISOString(),
            ["end_date"]: endDate.toISOString(),
            ["water_meter_id"]: variableValue
        };
        return this.execute<T>("post", `/water-meters/get-values`, body);
    }

    getDroughtIndices<T>(config: object) {
        const body = {
            ...config
        };

        return this.execute<T>(
            "post",
            "/drought-indices/get-drought-indices",
            body
        );
    }

    getSystemUnits<T>() {
        return this.execute<T>("get", "/system-unit/get-values");
    }

    getUserVerify<T>() {
        return this.execute<T>("get", "/auth/verify");
    }
}

const apiService = new APIService();
export const APIServicePlugin = {
    install: (Vue: typeof _Vue) => {
        /**
         * Add api-services globally and instance referenced
         */
        Vue.$api = apiService;
        Vue.prototype.$api = apiService;
    }
};
