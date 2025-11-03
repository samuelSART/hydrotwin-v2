<template>
    <BaseDialog
        v-model="dialogShown"
        :loading="loading"
        :title="pointInfo.name"
        :subtitle="pointInfo.type"
        @on-close="handleDialogClosed"
    >
        <template #form>
            <BasicForm
                v-model="formFilter"
                :timeRangesOptions="timeRangeOptions"
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
    ForecastValue,
    WaterBody,
    TypedVariableValue
} from "@/interfaces";
import * as types from "@/store/types";
import { EXPORT_PLOT_SVG } from "@/config";
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
    pointInfo!: WaterBody;

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

    async fetchPlotData({ startDate, endDate }) {
        this.loading = true;

        try {
            this.clearChart();

            const variableValues = await this.$api.getWaterMetersValues<
                VariableValueResponse
            >(this.variableCode, startDate, endDate);

            if (variableValues.ok) {
                this.updateVariableDataPlot(
                    variableValues.data,
                    this.variableCode
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
        this.fetchPlotData({
            startDate: config.startDate,
            endDate: config.endDate
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

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>

<style scoped></style>
