<template>
    <BaseDialog
        v-model="dialogShown"
        :loading="loading"
        :title="pointInfo.denomination"
        :subtitle="pointInfo.aquifer"
        @on-close="handleDialogClosed"
    >
        <template #form>
            <BasicForm
                v-model="formFilter"
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
import { Component, Vue, ModelSync, Prop, Ref } from "vue-property-decorator";
import { mapMutations } from "vuex";

import {
    getLineChartOption,
    getEmptyOption,
    getForecastingSeries
} from "@/config/charts";
import OptionChart from "@/components/charts/OptionChart.vue";
import {
    FormBtnAction,
    VariableValue,
    VariableValueResponse,
    ForecastResponse,
    ForecastValue,
    TypedVariableValue
} from "@/interfaces";
import * as types from "@/store/types";
import { cpTimeRangesPieConfig } from "@/pages/piezometry/cppiezometersconfig";
import { EXPORT_PLOT_SVG } from "@/config";
import { downloadCSV, exportDataToCSV } from "@/utils";

const TIME_RANGE = new Map<string, string>([
    ["7", "lastWeek"],
    ["14", "lastTwoWeeks"],
    ["30", "lastMonth"],
    ["90", "lastThreeMonths"],
    ["180", "lastSixMonths"],
    ["365", "lastYear"]
]);

const PREDICTION_RANGE = new Map<number, string>([
    [1, "forecastingTypeStandard"]
]);

// add [init year, init hydro year, init control] options
for (const cpTimeRange of cpTimeRangesPieConfig) {
    if (cpTimeRange.diffDays) {
        TIME_RANGE.set(cpTimeRange.diffDays().toString(), cpTimeRange.range);
    }
}
TIME_RANGE.set("custom", "custom");

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
export default class CPPiezometerDialog extends Vue {
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @ModelSync("dialogShownValue", "change", { type: Boolean })
    dialogShown!: boolean;

    @Prop({ type: Object, required: true })
    pointInfo!: Partial<{
        aquifer: string;
        denomination: string;
    }>;

    @Prop({ type: String, required: true })
    variableCode!: string;

    @Ref("chart") readonly chart!: OptionChart;

    pointOption: EChartsOption = {};
    loading = false;

    formFilter = {
        valid: false,
        timeRange: "365",
        customTimeRange: [],
        forecasting: 1
    };

    async fetchPlotData({ startDate, endDate, forecasting }) {
        this.loading = true;

        try {
            const reqBody = {
                type: "custom",
                range: {
                    start: startDate,
                    end: endDate
                }
            };

            this.clearChart();

            const variableValues = await this.$api.getCPPiezometersValues<
                VariableValueResponse
            >([this.variableCode], reqBody);

            let forecastingRes: ForecastResponse | undefined = undefined;

            if (forecasting) {
                forecastingRes = await this.$api.getForecast<ForecastResponse>(
                    this.variableCode,
                    forecasting,
                    "corp"
                );
            }

            if (variableValues.ok) {
                this.updateVariableDataPlot(
                    variableValues.data,
                    this.variableCode,
                    forecastingRes?.data
                );
            }
        } catch (error) {
            if (error instanceof Error) {
                console.log(error);
                this.showError("Error fetching data");
            }
        } finally {
            this.loading = false;
        }
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
    }

    /**
     * form refresh button event
     */
    handleFormRefresh(config: FormBtnAction) {
        this.fetchPlotData({
            startDate: config.startDate,
            endDate: config.endDate,
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

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>

<style scoped></style>
