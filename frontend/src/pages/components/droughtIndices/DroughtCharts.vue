<template>
    <div class="my-5">
        <v-row class="d-flex justify-center ma-0">
            <v-col class="my-0 py-0" xs="6" sm="5" md="4">
                <v-autocomplete
                    dense
                    v-model="subSystem"
                    :items="subSystems"
                    :label="$t('droughtIndices.subSystem')"
                ></v-autocomplete>
            </v-col>
            <v-col class="my-0 py-0" xs="6" sm="5" md="4">
                <v-btn
                    color="secondary"
                    class="white--text"
                    @click="fetchDroughtIndices"
                    block
                >
                    {{ $t("chart.generateChart") }}
                    <v-icon right dark>mdi-refresh</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row class="d-flex justify-center ma-0">
            <OptionChart
                ref="chart"
                height="calc(100vh - 400px)"
                width="calc(100vw - 350px)"
                :chart-options="droughtChartOption"
            />
        </v-row>
    </div>
</template>

<script lang="ts">
import { Component, Vue, Ref } from "vue-property-decorator";
import { EChartsOption } from "echarts";
import { mapMutations } from "vuex";

import { DroughtIndicesResponse } from "@/interfaces";
import OptionChart from "../charts/OptionChart.vue";
import { VariableValue } from "@/interfaces";
import { getLineChartOption, getEmptyOption } from "@/config/charts";
import * as types from "@/store/types";

@Component({
    components: {
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class DroughtCharts extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @Ref("chart") readonly chart!: OptionChart;

    droughtChartOption: EChartsOption = {};

    chartData;

    subSystems = ["Cuenca", "Trasvase", "Global"];

    subSystem = "Cuenca";

    async fetchDroughtIndices() {
        try {
            this.setProgressBar(true);
            const allData = {
                type: "all"
            };

            const droughtIndices = await this.$api.getDroughtIndices<
                DroughtIndicesResponse
            >(allData);

            if (droughtIndices.ok) {
                this.chartData = droughtIndices.data.map(droughtIndex => [
                    droughtIndex.FECHA,
                    droughtIndex[this.subSystem.toUpperCase()]
                ]);
                this.updateAemetVariablePlot(this.chartData);
            }
        } catch (error) {
            this.setInfoMessage({
                shown: true,
                text: this.$t("droughtIndices.noData").toString()
            });
        } finally {
            this.setProgressBar(false);
        }
    }

    /**
     * Plot aemet variable
     */
    updateAemetVariablePlot(values: VariableValue[]): void {
        if (!values || !values.length) {
            this.droughtChartOption = {
                ...getEmptyOption(`${this.$t("chart.noData")}`)
            };
            return;
        }

        this.droughtChartOption = getLineChartOption({});

        /**
         * XAxis
         */
        this.droughtChartOption.xAxis = {
            ...this.droughtChartOption.xAxis,
            data: undefined,
            type: "time",
            splitArea: {
                show: false
            }
        };

        /**
         * YAxis
         */
        this.droughtChartOption.yAxis = {
            ...this.droughtChartOption.yAxis,
            name: this.$t("droughtIndices.droughtIndices").toString(),
            nameLocation: "middle",
            nameGap: 40,
            min: 0,
            max: 1,
            nameTextStyle: {
                fontSize: 20,
                fontWeight: "bold",
                color: "#333"
            }
        };

        /**
         * dataZoom
         */
        this.droughtChartOption.dataZoom = [
            {
                type: "inside",
                start: 90,
                end: 100
            },
            {
                start: 90,
                end: 100
            }
        ];

        /**
         * Grid
         */
        this.droughtChartOption.grid = {
            ...this.droughtChartOption.grid,
            top: 70,
            left: 40,
            bottom: 50
        };

        this.droughtChartOption.title = {
            left: "center",
            text: `${this.$t("droughtIndices.droughtIndices")} - ${
                this.subSystem
            }`
        };

        this.droughtChartOption.visualMap = {
            top: 40,
            right: 20,
            orient: "horizontal",
            itemGap: 30,
            pieces: [
                {
                    gt: 0,
                    lte: 0.15,
                    color: "red",
                    label: this.$t("droughtIndices.emergency").toString()
                },
                {
                    gt: 0.15,
                    lte: 0.3,
                    color: "darkOrange",
                    label: this.$t("droughtIndices.alert").toString()
                },
                {
                    gt: 0.3,
                    lte: 0.5,
                    color: "gold",
                    label: this.$t("droughtIndices.preAlert").toString()
                },
                {
                    gt: 0.5,
                    color: "yellowGreen",
                    label: this.$t("droughtIndices.normal").toString()
                }
            ]
        };

        this.droughtChartOption.toolbox = {
            feature: {
                dataZoom: {
                    yAxisIndex: "none"
                },
                restore: {}
            }
        };

        const serieCopy = this.droughtChartOption.series
            ? { ...this.droughtChartOption.series[0] }
            : {};

        this.droughtChartOption.series = [];
        this.droughtChartOption.series.push({
            ...serieCopy,
            name: this.$t("measPointDialog.value"),
            data: values,
            symbol: "none",
            markLine: {
                silent: true,
                label: {
                    position: "start",
                    fontWeight: "bold",
                    fontSize: 14
                },
                data: [
                    {
                        yAxis: 0.15,
                        lineStyle: {
                            color: "chocolate",
                            type: "dashed"
                        }
                    },
                    {
                        yAxis: 0.3,
                        lineStyle: {
                            color: "orange",
                            type: "dashed"
                        }
                    },
                    {
                        yAxis: 0.5,
                        lineStyle: {
                            color: "yellow",
                            type: "dashed"
                        }
                    }
                ]
            }
        });
    }

    /**
     * Show error message
     * @param {string} error Error message
     * @return {void}
     */
    showError(error: string): void {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>
