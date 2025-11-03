<template>
    <OptionChart
        ref="chart"
        height="400px"
        dashboard
        :chart-options="deficitChartOption"
    />
</template>

<script lang="ts">
import { Vue, Component, Ref, PropSync, Watch } from "vue-property-decorator";
import { EChartsOption, MarkAreaComponentOption } from "echarts";

import OptionChart from "@/components/charts/OptionChart.vue";
import { OptimizerPlotData } from "@/interfaces";
@Component({
    components: {
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    }
})
export default class WaterDeficitChart extends Vue {
    @Ref("chart") readonly chartDeficit!: OptionChart;
    deficitChartOption: EChartsOption = {};

    @PropSync("plotData", { type: Object })
    data!: OptimizerPlotData;

    negativeDates: MarkAreaComponentOption = {
        itemStyle: {
            color: "rgba(255, 173, 177, 0.4)"
        },
        data: []
    };

    @Watch("data.date")
    async onDataChange() {
        this.clearChart();
        if (this.data.date.length > 0) {
            this.computeDeficit();
            this.loadDeficitChart();
        }
    }

    mounted() {
        this.clearChart();
        if (this.data != undefined) {
            if (this.data.date.length > 0) {
                this.computeDeficit();
                this.loadDeficitChart();
            }
        }
    }

    /**
     * Clear chart
     * @return {void}
     */
    clearChart(): void {
        if (!this.chartDeficit) return;
        this.chartDeficit.clearChart();
    }

    computeDeficit(): void {
        this.negativeDates.data = [];
        for (let i = 0; i < this.data.date.length; i++) {
            const deficit = this.data.planned[i] - this.data.demand[i];
            if (deficit < 0) {
                const start = this.data.date[i];
                if (i + 1 < this.data.date.length) {
                    const end = this.data.date[i + 1];
                    this.negativeDates.data?.push([
                        {
                            name: "",
                            xAxis: start
                        },
                        {
                            xAxis: end
                        }
                    ]);
                }
            }
        }
    }

    loadDeficitChart(): void {
        this.deficitChartOption = {
            title: {
                text: String(this.$t('waterDeficitChart.chartTitle')),
                left: "center"
            },
            tooltip: {
                trigger: "axis",
                formatter: (params: any) => {
                    let result = `${params[0].name} <br>`;
                    params.forEach((param: any) => {
                        if (
                            param.seriesName != "Lower Uncertainty" &&
                            param.seriesName != "Upper Uncertainty"
                        ) {
                            result += `${param.marker} ${
                                param.seriesName
                            }: ${param.value.toFixed(
                                4
                            )} hm<sup>3</sup> <br/>`;
                        }
                    });
                    return result;
                }
            },
            toolbox: {
                feature: {
                    dataZoom: {
                        yAxisIndex: "none"
                    },
                    restore: {}
                }
            },
            legend: {
                data: [
                String(this.$t('waterDeficitChart.demand')),
                String(this.$t('waterDeficitChart.flow')),
                    this.data?.oldPlan != undefined ? String(this.$t('waterDeficitChart.nonOptimized')) : ""
                ],
                left: 10,
                top: 30
            },
            xAxis: {
                type: "category",
                data: this.data.date
            },
            yAxis: [
                {
                    type: "value",
                    position: "left",
                    axisLabel: {
                        formatter: "{value}"
                    }
                }
            ],
            series: [
                {
                    name: String(this.$t('waterDeficitChart.demand')),
                    type: "line",
                    smooth: false,
                    step: "end",
                    data: this.data.demand
                },

                {
                    name: "Deficit",
                    type: "line",
                    markArea: this.negativeDates
                },
                {
                    name: "Lower Uncertainty",
                    type: "line",
                    data: this.data.incertLow,
                    smooth: true,
                    color: "grey",
                    lineStyle: {
                        opacity: 0
                    },
                    stack: "confidence-band",
                    symbol: "none"
                },
                {
                    name: String(this.$t('waterDeficitChart.flow')),
                    type: "line",
                    smooth: false,
                    step: "end",
                    data: this.data.planned
                },
                {
                    name: "Upper Uncertainty",
                    type: "line",
                    data: this.data.incertHigh,
                    color: "grey",
                    smooth: true,
                    lineStyle: {
                        opacity: 0
                    },
                    areaStyle: {
                        color: "#cccc"
                    },
                    stack: "confidence-band",
                    symbol: "none"
                },
                {
                    name: String(this.$t('waterDeficitChart.nonOptimized')),
                    type: "line",
                    color: "grey",
                    step: "end",
                    data:
                        this.data?.oldPlan != undefined
                            ? this.data.oldPlan?.planned
                            : []
                }
            ]
        };
    }
}
</script>
