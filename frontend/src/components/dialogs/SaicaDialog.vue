<template>
    <BaseDialog
        v-model="dialogShown"
        :loading="loading"
        :title="pointInfo.denomination"
        :subtitle="pointInfo.description"
        @on-close="handleDialogClosed"
    >
        <template #form>
            <BasicForm
                v-model="formFilter"
                :variablesOptions="variableOptions"
                :timeRangesOptions="timeRangeOptions"
                :predictionsOptions="predictionOptions"
                @on-refresh="handleFormRefresh"
            />
        </template>
        <template #plot>
            <OptionChart
                ref="chart"
                height="400px"
                :chart-options="pointOption"
                data-testid=""
            />
        </template>
    </BaseDialog>
</template>

<script lang="ts">
import { EChartsOption } from "echarts";
import {
    Component,
    Vue,
    ModelSync,
    Prop,
    Ref,
    Watch
} from "vue-property-decorator";
import { mapMutations } from "vuex";

import OptionChart from "@/components/charts/OptionChart.vue";
import {
    getLineChartOption,
    getEmptyOption,
    getForecastingSeries
} from "@/config/charts";
import {
    FormBtnAction,
    MeasurementPoint,
    VariableValue,
    VariableValueResponse,
    ForecastResponse,
    ForecastValue,
    Variable,
    TypedVariableValue
} from "@/interfaces";
import * as types from "@/store/types";
import { EXPORT_PLOT_SVG, VARIABLE_TYPOLOGIES } from "@/config";
import { downloadCSV, exportDataToCSV } from "@/utils";

const TIME_RANGE = new Map<string, string>([
    ["7", "lastWeek"],
    ["14", "lastTwoWeeks"],
    ["30", "lastMonth"],
    ["90", "lastThreeMonths"],
    ["180", "lastSixMonths"],
    ["365", "lastYear"],
    ["custom", "custom"]
]);

const FORECAST_TYPO_NAMES = new Map<string, string>([
    ["2", "PH"],
    ["3", "Conductividad"],
    ["4", "OxígenoDisuelto"],
    ["7", "SAC"],
    ["T", "Temperatura"],
    ["H", "Humedad"],
    ["R", "PuntoRocío"],
    ["P", "Pluviometría"]
]);

const PREDICTION_RANGE = new Map<number, string>([
    [1, "forecastingType1"],
    [6, "forecastingType6"]
]);

@Component({
    components: {
        BaseDialog: () => import("@/components/dialogs/BaseDialog.vue"),
        OptionChart: () => import("@/components/charts/OptionChart.vue"),
        BasicForm: () => import("@/components/forms/BasicForm.vue")
    },
    methods: {
        ...mapMutations({
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class SaicaDialog extends Vue {
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @ModelSync("dialogShownValue", "change", { type: Boolean })
    dialogShown!: boolean;

    @Prop({ type: Object, required: true })
    pointInfo!: Partial<MeasurementPoint>;

    @Prop({ type: String, required: true })
    variableCode!: string;

    @Ref("chart") readonly chart!: OptionChart;

    pointOption: EChartsOption = {};
    loading = false;

    sortedPointVariables: Variable[] = [];

    formFilter = {
        valid: false,
        variable: "N",
        timeRange: "365",
        customTimeRange: [],
        forecasting: 1
    };

    @Watch("dialogShown")
    async onDialogShown() {
        if (!this.dialogShown) return;

        this.sortedPointVariables = this.getSortedPointVariables();

        if (this.sortedPointVariables?.length) {
            this.formFilter.variable = this.sortedPointVariables[0].typology;
        }
    }

    /**
     * Get a new array sorted with FORECAST_TYPO_NAMES
     * variables as priority variables
     */
    getSortedPointVariables() {
        this.sortedPointVariables = [];

        const priorityVars: Variable[] = [];
        const nonPriorityVars: Variable[] = [];

        for (const pointVariable of this.pointInfo.variables || []) {
            if (FORECAST_TYPO_NAMES.has(pointVariable.typology)) {
                priorityVars.push({
                    ...pointVariable
                });
                continue;
            }

            nonPriorityVars.push({
                ...pointVariable
            });
        }

        return [...priorityVars, ...nonPriorityVars];
    }

    async fetchPlotData({ startDate, endDate, variable, forecasting, target }) {
        this.loading = true;

        try {
            const variableValues = await this.$api.getVariablesValues<
                VariableValueResponse
            >([variable], startDate, endDate, "mean", "1d");

            this.clearChart();

            let forecastingRes: ForecastResponse | void = undefined;

            if (forecasting) {
                const station = this.pointInfo.denomination || "-";
                forecastingRes = await this.$api
                    .getSaicaForecast<ForecastResponse>(
                        station,
                        target,
                        forecasting
                    )
                    .catch(error => {
                        if (error instanceof Error) {
                            console.log("[SaicaDialog]", error);
                            const errorKey = `qualitySaica.error.${error.message}`;
                            const errorTxt = this.$te(errorKey)
                                ? this.$t(errorKey).toString()
                                : "No data for this forecasting";
                            this.showError(errorTxt);
                        }
                    });
            }

            const forecastingData = forecastingRes
                ? forecastingRes.data
                : undefined;

            if (variableValues.ok) {
                this.updateVariableDataPlot(
                    variableValues.data,
                    variable,
                    forecastingData
                );
            }
        } catch (error) {
            if (error instanceof Error) {
                console.log("[SaicaDialog]", error);
                this.showError("Error fetching plot data");
            }
        } finally {
            this.loading = false;
        }
    }

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }

    /**
     * Clear chart
     */
    clearChart() {
        if (!this.chart) return;
        this.chart.clearChart();
    }

    /**
     * Update echarts plot with fetched data
     */
    updateVariableDataPlot(
        values: VariableValue[],
        variableCode: string,
        forecastingData: ForecastValue[] | undefined = undefined
    ): void {
        if (
            (!values || !values.length) &&
            (!forecastingData || !forecastingData.length)
        ) {
            this.pointOption = {
                ...getEmptyOption(`${this.$t("chart.noData")}`)
            };
            return;
        }

        this.pointOption = { ...getLineChartOption({}) };

        /**
         * XAxis
         */
        this.pointOption.xAxis = {
            ...this.pointOption.xAxis,
            data: undefined,
            type: "time",
            splitArea: {
                show: false
            }
        };

        this.pointOption.toolbox = {
            feature: {
                dataZoom: {
                    yAxisIndex: "none"
                },
                restore: {},
                myExport: {
                    show: true,
                    title: "csv",
                    icon: EXPORT_PLOT_SVG,
                    onclick: () => {
                        const rData: TypedVariableValue[] = values.map(
                            (value: VariableValue) => {
                                return { ...value, type: "real" };
                            }
                        );

                        let fData: TypedVariableValue[] = [];
                        if (forecastingData) {
                            fData = forecastingData.map(
                                ({ ds, yhat }: ForecastValue) => {
                                    return {
                                        _time: ds,
                                        _value: yhat,
                                        type: "predicted",
                                        variableCode: variableCode
                                    };
                                }
                            );
                        }

                        const csvData = exportDataToCSV(
                            [rData, fData],
                            variableCode
                        );

                        downloadCSV(csvData, variableCode);
                    }
                }
            }
        };

        /**
         * Data as arrays of [{timestamp}, {value}]
         */
        const data = values.map(({ _time, _value }: VariableValue) => [
            +new Date(_time),
            _value.toFixed(3)
        ]);
        const serieCopy = this.pointOption.series
            ? { ...this.pointOption.series[0] }
            : {};

        this.pointOption.series = [];
        this.pointOption.series.push({
            ...serieCopy,
            name: this.$t("measPointDialog.value"),
            data,
            symbol: "none"
        });

        /**
         * Forecasting
         */
        if (forecastingData) {
            const fcSeries = getForecastingSeries(forecastingData, {
                serieCopy,
                areaColor: "#ccc"
            });

            this.pointOption.series.push(...fcSeries);
        }
    }

    /**
     * form refresh button event
     */
    handleFormRefresh(config: FormBtnAction) {
        const selVariable = this.pointInfo.variables?.find(
            variable => variable.typology === config.variable
        );

        if (!selVariable) return;

        this.fetchPlotData({
            startDate: config.startDate,
            endDate: config.endDate,
            variable: selVariable.code,
            target: FORECAST_TYPO_NAMES.get(selVariable.typology) || "",
            forecasting: config.forecasting
        });
    }

    /**
     * Clear chart when dialog is closed
     */
    handleDialogClosed() {
        this.clearChart();
    }

    /**
     * Variable options
     */
    get variableOptions() {
        return this.sortedPointVariables.map(v => {
            return {
                value: v.typology,
                text: this.$t(
                    `form.variableTypology.${VARIABLE_TYPOLOGIES.get(
                        v.typology
                    )}`
                )
            };
        });
    }

    /**
     * Time ranges options
     */
    get timeRangeOptions() {
        return Array.from(TIME_RANGE).map(([key, value]) => {
            return {
                value: key,
                text: this.$t(`form.timeRange.${value}`)
            };
        });
    }

    /**
     * Prediction ranges options
     */
    get predictionOptions() {
        return Array.from(PREDICTION_RANGE).map(([key, value]) => {
            return {
                value: key,
                text: this.$t(`form.predictions.${value}`)
            };
        });
    }
}
</script>

<style scoped></style>
