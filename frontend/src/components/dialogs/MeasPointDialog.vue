<template>
    <BaseDialog
        v-model="dialogShown"
        :loading="loading"
        :title="dialogTitle"
        :subtitle="measPointInfo.description"
        @on-close="handleDialogClosed"
    >
        <template #form>
            <BasicForm
                v-model="formFilter"
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
                :chart-options="measPointOption"
                data-testid=""
            />
        </template>
    </BaseDialog>
</template>

<script lang="ts">
import { EChartsOption } from "echarts";
import { Component, Vue, ModelSync, Prop, Ref } from "vue-property-decorator";
import { mapMutations } from "vuex";

import {
    getLineChartOption,
    getEmptyOption,
    getForecastingSeries
} from "@/config/charts";
import {
    EnvironmentalFlow,
    MeasurementPoint,
    VariableValue,
    VariableValueResponse,
    FormBtnAction,
    ForecastResponse,
    ForecastValue,
    TypedVariableValue,
    SimulationResponse,
    DroughtIndicesResponse,
    DroughtIndices
} from "@/interfaces";
import OptionChart from "@/components/charts/OptionChart.vue";
import {
    DroughtStates,
    ENV_FLOW_PERIODS,
    SYSTEM_ZONES
} from "@/pages/EnvironmentalFlow.vue";
import * as types from "@/store/types";
import { downloadCSV, exportDataToCSV } from "@/utils";
import { EXPORT_PLOT_SVG } from "@/config";

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
export default class MeasPointDialog extends Vue {
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @ModelSync("dialogShownValue", "change", { type: Boolean })
    dialogShown!: boolean;

    @Prop({ type: Object, required: true })
    measPointInfo!: Partial<MeasurementPoint>;

    @Prop({ type: String, required: true })
    variableCode!: string;

    @Prop({ type: Array, required: true, default: () => [] })
    environmentFlow!: EnvironmentalFlow[];

    @Ref("chart") readonly chart!: OptionChart;

    measPointOption: EChartsOption = {};
    loading = false;

    formFilter = {
        valid: false,
        variable: "N",
        timeRange: "365",
        customTimeRange: [],
        forecasting: 1,
        simulation: 0
    };

    async fetchPlotData({ startDate, endDate, forecasting, simulation }) {
        this.loading = true;

        try {
            /**
             * Real data
             */
            const variableValues = await this.$api.getVariablesValues<
                VariableValueResponse
            >([this.variableCode], startDate, endDate, "mean", "1d");

            /**
             * Drought indices
             */
            const droughtIndices = await this.$api.getDroughtIndices<
                DroughtIndicesResponse
            >({
                type: "custom",
                range: {
                    start: startDate.toISOString(),
                    end: endDate.toISOString()
                }
            });

            /**
             * Reset chart
             */
            this.clearChart();

            /**
             * Forecasting
             */
            let forecastingRes: ForecastResponse | undefined = undefined;

            if (forecasting) {
                forecastingRes = await this.$api.getForecast<ForecastResponse>(
                    this.variableCode,
                    forecasting
                );
            }

            /**
             * Simulation
             */
            let simulationRes: SimulationResponse | undefined = undefined;
            if (simulation !== undefined) {
                simulationRes = await this.$api.getSimulation<
                    SimulationResponse
                >(
                    [this.variableCode],
                    startDate,
                    endDate,
                    simulation,
                    "mean",
                    "1d"
                );
            }

            /**
             * Plot chart
             */
            if (variableValues.ok) {
                this.updateVariableDataPlot(
                    variableValues.data,
                    this.variableCode,
                    forecastingRes?.data,
                    simulationRes?.data,
                    droughtIndices?.data
                );
            }
        } catch (error) {
            if (error instanceof Error) {
                console.error(error);
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
     * Clear chart to leave a blank plot
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
        forecastingData: ForecastValue[] | undefined = undefined,
        simulationData: VariableValue[] | undefined = undefined,
        droughtIndices: DroughtIndices[] | undefined = undefined
    ): void {
        if (
            (!values || !values.length) &&
            (!forecastingData || !forecastingData.length)
        ) {
            this.measPointOption = {
                ...getEmptyOption(`${this.$t("chart.noData")}`)
            };
            return;
        }

        const envFlowData = this.environmentFlow.find(
            ef => ef.variable === variableCode
        );

        this.measPointOption = { ...getLineChartOption({}) };

        /**
         * XAxis
         */
        this.measPointOption.xAxis = {
            ...this.measPointOption.xAxis,
            data: undefined,
            type: "time",
            splitArea: {
                show: false
            }
        };

        /**
         * Activate legend to hide/show generator flow
         */
        const dataSeriesName = this.$t("measPointDialog.value");
        const generatorSeriesName = this.$t("measPointDialog.generatorFlow");
        const limitSeriesname = this.$t("measPointDialog.environmentalFlow");
        const simulationsSeriesname = this.$t(
            "form.simulations.simulationSeries"
        );
        this.measPointOption.legend = {
            data: [
                dataSeriesName,
                generatorSeriesName,
                limitSeriesname,
                simulationsSeriesname
            ]
        };

        /**
         * Data as arrays of [{timestamp}, {value}]
         */
        const data = values.map(({ _time, _value }: VariableValue) => [
            +new Date(_time),
            _value.toFixed(3)
        ]);
        const serieCopy = this.measPointOption.series
            ? { ...this.measPointOption.series[0] }
            : {};

        this.measPointOption.series = [];
        this.measPointOption.series.push({
            ...serieCopy,
            name: dataSeriesName,
            data,
            symbol: "none"
        });

        this.measPointOption.yAxis = {
            ...this.measPointOption.yAxis,
            name: `${this.$t("form.variableTypology.caudal")} (m³/s)`,
            nameLocation: "middle",
            nameGap: 23,
            nameTextStyle: {
                color: "#000000",
                fontWeight: "bold"
            }
        };

        this.measPointOption.toolbox = {
            feature: {
                dataZoom: {
                    brushStyle: {
                        color: "gray",
                        opacity: 0.25
                    }
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
         * Limits series
         */
        if (envFlowData) {
            droughtIndices?.reverse();

            const limitsData = values.map(({ _time }: VariableValue) => {
                const date = new Date(_time);
                const limit = this.getMonthLimit(
                    date,
                    envFlowData,
                    droughtIndices
                );

                return [+date, limit?.limit, limit?.inDrought || false];
            });

            /**
             * Search for droughtPeriods to paint them red
             */
            const droughtPeriods = limitsData.reduce(
                (accum, current, index, original) => {
                    const [ts, , inDrought] = current;
                    if (inDrought && index === 0) {
                        accum.push({
                            gt: ts,
                            color: "red"
                        });
                    }

                    if (index !== 0) {
                        if (original[index - 1][2] !== inDrought) {
                            if (!inDrought) {
                                accum[accum.length - 1] = {
                                    ...accum[accum.length - 1],
                                    lte: ts
                                };
                            } else {
                                accum.push({
                                    gt: ts,
                                    color: "red"
                                });
                            }
                        }
                    }

                    if (index === original.length - 1 && accum.length === 1) {
                        if (!("lte" in accum[accum.length - 1])) {
                            accum[accum.length - 1] = {
                                ...accum[accum.length - 1],
                                lte: ts
                            };
                        }
                    }

                    return accum;
                },
                []
            );

            this.measPointOption.series.push({
                ...serieCopy,
                name: limitSeriesname,
                data: limitsData,
                symbol: "none",
                color: "#848484",
                lineStyle: {
                    type: "dashed",
                    width: 1
                },
                emphasis: false
            });

            this.measPointOption.visualMap = {
                type: "piecewise",
                show: false,
                seriesIndex: 1,
                dimension: 0,
                outOfRange: {
                    color: "#848484"
                },
                pieces: droughtPeriods
            };
        }

        /**
         * Caudal generador
         * If exists, create a markline displaying the generator flow value
         */
        const generatorFlow = envFlowData?.water_body.generator_flow;
        if (generatorFlow) {
            this.measPointOption.series.push({
                ...serieCopy,
                symbol: "none",
                name: generatorSeriesName,
                data: data.map(([_time]) => {
                    return [_time, generatorFlow];
                }),
                lineStyle: {
                    type: "dashed",
                    width: 1
                },
                emphasis: false
            });
        }

        /**
         * Forecasting
         */
        if (forecastingData) {
            const fcSeries = getForecastingSeries(forecastingData, {
                serieCopy,
                areaColor: "#ccc"
            });

            this.measPointOption.series.push(...fcSeries);
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

            this.measPointOption.series.push({
                ...serieCopy,
                name: simulationsSeriesname,
                data: sData,
                symbol: "none"
            });
        }
    }

    /**
     * get defined limit for actual month
     */
    getMonthLimit(
        valueDate: Date,
        envFlowData: EnvironmentalFlow,
        droughtIndices: DroughtIndices[] | undefined = undefined
    ) {
        const month = valueDate.getMonth();
        const flowSM = envFlowData.masa_estrategica;
        let period: string | undefined = undefined;
        let inDrought = false;

        /**
         * Get sistem zone property
         * UTS_I_Principal_Situacion, UTS_II_Cabecera_Situacion ...
         */
        const flowSystem = envFlowData.sistema;
        const systemZone = SYSTEM_ZONES.get(flowSystem);

        /**
         * -----------------------------------------
         * Search for inDrought state
         * -----------------------------------------
         */

        if (!flowSM && droughtIndices && droughtIndices.length && systemZone) {
            inDrought = this.checkInDroughtMode(
                valueDate,
                droughtIndices,
                systemZone
            );
        }

        /**
         * Get period key depending on inDrought variable
         */
        for (const [key, config] of ENV_FLOW_PERIODS) {
            const { months } = config;
            if (months.indexOf(month) !== -1) {
                period = inDrought ? key + "_seq" : key;
                break;
            }
        }

        if (period) {
            return {
                limit: envFlowData[period],
                inDrought
            };
        }

        return undefined;
    }

    /**
     * Check if value's date is in drought state (Prolonged)
     */
    checkInDroughtMode(
        valueDate: Date,
        droughtIndices: DroughtIndices[],
        systemZone: string
    ) {
        let inDrought = false;

        /**
         * There is only record so use only this system zone state
         */
        if (droughtIndices.length === 1) {
            if (droughtIndices[0][systemZone] === DroughtStates.Prolonged) {
                return true;
            }
        }

        /**
         * Search for value's limit
         */
        let index: number | undefined = undefined;

        for (let i = 0; i < droughtIndices.length; i++) {
            const droughtIndice = droughtIndices[i];
            const droughtIndiceDate = new Date(droughtIndice.FECHA);
            if (valueDate < droughtIndiceDate) {
                index = i - 1;
                break;
            }
        }

        /**
         * Apply latest record
         */
        if (index === undefined) index = droughtIndices.length - 1;

        if (
            index >= 0 &&
            droughtIndices[index][systemZone] === DroughtStates.Prolonged
        ) {
            inDrought = true;
        }

        return inDrought;
    }

    /**
     * form refresh button event
     */
    handleFormRefresh(config: FormBtnAction) {
        this.fetchPlotData({
            startDate: config.startDate,
            endDate: config.endDate,
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

    get dialogTitle() {
        return `${this.measPointInfo.denomination} (${this.variableCode})`;
    }
}
</script>

<style scoped></style>
