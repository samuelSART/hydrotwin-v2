<template>
    <BaseDialog
        v-model="dialogShown"
        :loading="loading"
        :title="`${pointInfo.denomination} (${variableCode})`"
        :subtitle="pointInfo.description"
        @on-close="handleDialogClosed"
    >
        <template #form>
            <BasicForm
                ref="basicForm"
                v-model="formFilter"
                :variablesOptions="variableOptions"
                :timeRangesOptions="timeRangeOptions"
                :predictionsOptions="predictionOptions"
                :simulationsOptions="simulationOptions"
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
    TypedVariableValue,
    SimulationResponse
} from "@/interfaces";
import * as types from "@/store/types";
import { EXPORT_PLOT_SVG, VARIABLE_TYPOLOGIES } from "@/config";
import { downloadCSV, exportDataToCSV, getTypologyUnitText } from "@/utils";

export const VARIABLES = ["N", "1", "3", "B", "C"];

const TIME_RANGE = new Map<string, string>([
    ["7", "lastWeek"],
    ["14", "lastTwoWeeks"],
    ["30", "lastMonth"],
    ["90", "lastThreeMonths"],
    ["180", "lastSixMonths"],
    ["365", "lastYear"],
    ["custom", "custom"]
]);

const PREDICTION_RANGE = new Map<number, string>([
    [1, "forecastingType1"],
    [2, "forecastingType2"],
    [3, "forecastingType3"],
    [4, "forecastingType4"],
    [5, "forecastingType5"]
]);

const SIMULATION_RANGE = new Map<number, string>([
    [0, "simulationType1"],
    [1, "simulationType2"]
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
export default class PiezometerDialog extends Vue {
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @ModelSync("dialogShownValue", "change", { type: Boolean })
    dialogShown!: boolean;

    @Prop({ type: Object, required: true })
    pointInfo!: Partial<MeasurementPoint>;

    @Prop({ type: String, required: true })
    variableCode!: string;

    @Ref("basicForm") basicFormRef;
    @Ref("chart") readonly chart!: OptionChart;

    pointOption: EChartsOption = {};
    loading = false;

    formFilter = {
        valid: false,
        variable: undefined,
        timeRange: undefined,
        customTimeRange: [],
        predictionEnabled: true,
        forecasting: 1,
        simulationEnabled: false,
        simulation: 0
    };

    @Watch("dialogShown")
    async onDialogShown() {
        if (!this.dialogShown) {
            this.reset();
            return;
        }
    }

    @Watch("formFilter.variable")
    onVariableChanged() {
        const typology = this.formFilter.variable;

        const levelTypology = "N";
        this.formFilter.simulationEnabled = typology === levelTypology;
    }

    /**
     * Reset from values and plot
     * @return {void}
     */
    reset(): void {
        this.formFilter = {
            valid: false,
            variable: undefined,
            timeRange: undefined,
            customTimeRange: [],
            predictionEnabled: true,
            forecasting: 1,
            simulationEnabled: false,
            simulation: 0
        };
        this.basicFormRef.resetValidation();
        if (this.chart) {
            this.chart.clearChart();
        }
    }

    async fetchPlotData({
        startDate,
        endDate,
        variable,
        typology,
        forecasting,
        simulation
    }) {
        this.loading = true;

        try {
            const variableValues = await this.$api.getVariablesValues<
                VariableValueResponse
            >([variable], startDate, endDate, "mean", "1d");

            this.clearChart();

            let forecastingRes: ForecastResponse | undefined = undefined;
            if (forecasting) {
                forecastingRes = await this.$api.getForecast<ForecastResponse>(
                    variable,
                    forecasting
                );
            }

            let simulationRes: SimulationResponse | undefined = undefined;
            if (simulation !== undefined) {
                simulationRes = await this.$api.getSimulation<
                    SimulationResponse
                >([variable], startDate, endDate, simulation, "mean", "1d");
            }

            if (variableValues.ok) {
                this.updateVariableDataPlot(
                    variableValues.data,
                    variable,
                    typology,
                    forecastingRes?.data,
                    simulationRes?.data
                );
            }
        } catch (error) {
            if (error instanceof Error) {
                console.log(error);
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
        typology: string,
        forecastingData: ForecastValue[] | undefined = undefined,
        simulationData: VariableValue[] | undefined = undefined
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
         * Legend
         */
        const dataSeriesName = this.$t("measPointDialog.value");
        const simulationsSeriesname = this.$t(
            "form.simulations.simulationSeries"
        );

        this.pointOption.legend = {
            data: [dataSeriesName, simulationsSeriesname]
        };

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

        /**
         * YAxis
         */
        const typologyText = getTypologyUnitText(typology);
        this.pointOption.yAxis = {
            ...this.pointOption.yAxis,
            name: typologyText,
            nameLocation: "middle",
            nameGap: 20,
            nameTextStyle: {
                color: "#000000",
                fontWeight: "bold"
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

                        let sData: TypedVariableValue[] = [];
                        if (simulationData) {
                            sData = simulationData.map(
                                (value: VariableValue) => {
                                    return { ...value, type: "simulated" };
                                }
                            );
                        }

                        const csvData = exportDataToCSV(
                            [rData, fData, sData],
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
            _value
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

        /**
         * Simulation
         */
        if (simulationData) {
            const sData = simulationData.map(
                ({ _time, _value }: VariableValue) => [
                    +new Date(_time),
                    _value.toFixed(3)
                ]
            );

            this.pointOption.series.push({
                ...serieCopy,
                name: simulationsSeriesname,
                data: sData,
                symbol: "none"
            });
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
            typology: selVariable.typology,
            forecasting: config.forecasting,
            simulation: config.simulation
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
        const pointVars = this.pointInfo.variables;
        return pointVars?.map(v => {
            return {
                value: v.typology,
                text:
                    this.$t(
                        `form.variableTypology.${VARIABLE_TYPOLOGIES.get(
                            v.typology
                        )}`
                    ) + ` (${v.code})`
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

    /**
     * Simulation ranges options
     */
    get simulationOptions() {
        return Array.from(SIMULATION_RANGE).map(([key, value]) => {
            return {
                value: key,
                text: this.$t(`form.simulations.${value}`)
            };
        });
    }
}
</script>

<style scoped></style>
