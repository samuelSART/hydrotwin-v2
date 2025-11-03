<template>
    <OptionChart
        ref="chart"
        height="400px"
        dashboard
        :chart-options="sourceDistributionChart"
    />
</template>

<script lang="ts">
import { Vue, Component, Ref, PropSync, Watch } from "vue-property-decorator";
import { EChartsOption } from "echarts";
import OptionChart from "@/components/charts/OptionChart.vue";
import { PlannerPlotData } from "@/interfaces";

@Component({
    components: {
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    }
})
export default class Planner extends Vue {
    @Ref("chart") readonly chartDistribution!: OptionChart;

    sourceDistributionChart: EChartsOption = {};

    @PropSync("plotData", { type: Object })
    data!: PlannerPlotData;

    @Watch("data.date")
    async onDataChange() {
        this.clearChart();
        if (this.data.date.length > 0) {
            this.loadSourceDistributionChart();
        }
    }

    mounted() {
        this.clearChart();
        if (this.data != undefined) {
            if (this.data.date.length > 0) {
                this.loadSourceDistributionChart();
            }
        }
    }

    /**
     * Clear chart
     * @return {void}
     */
    clearChart(): void {
        if (!this.chartDistribution) return;
        this.chartDistribution.clearChart();
    }

    loadSourceDistributionChart() {
        this.sourceDistributionChart = {
            title: {
                text: String(this.$t("sourceDistributionChart.chartTitle")),
                left: "center"
            },
            tooltip: {
                trigger: "axis",
                formatter: (params: any) => {
                    let result = `${params[0].name} <br>`;
                    params.forEach((param: any) => {
                        result += `${param.marker} ${param.seriesName}: ${(
                            param.value * 100
                        ).toFixed(4)}%<br/>`;
                    });
                    return result;
                }
            },
            toolbox: {
                feature: {
                    magicType: {
                        type: ["line", "bar"]
                    }
                }
            },
            xAxis: [
                {
                    type: "category",
                    data: this.data.date
                }
            ],
            yAxis: [
                {
                    show: false,
                    type: "value",
                    axisLabel: {
                        formatter: value => {
                            return (value * 100).toFixed(0) + "";
                        }
                    }
                }
            ],
            series: [
                {
                    name: String(this.$t('planner.superficial')),
                    type: "bar",
                    stack: "Water Type",
                    color: "#893448",
                    emphasis: {
                        focus: "series"
                    },
                    data: this.data.superficial
                },
                {
                    name: String(this.$t('planner.subterranea')),
                    type: "bar",
                    stack: "Water Type",
                    color: "#d95850",
                    emphasis: {
                        focus: "series"
                    },
                    data: this.data.subterranea
                },
                {
                    name: String(this.$t('planner.reutilizada')),
                    type: "bar",
                    stack: "Water Type",
                    color: "#eb8146",
                    emphasis: {
                        focus: "series"
                    },
                    data: this.data.reutilizada
                },
                {
                    name: String(this.$t('planner.trasvase')),
                    type: "bar",
                    stack: "Water Type",
                    color: "#ffb248",
                    data: this.data.trasvase,
                    emphasis: {
                        focus: "series"
                    }
                },
                {
                    name: String(this.$t('planner.desalada')),
                    type: "bar",
                    stack: "Water Type",
                    color: "#f2d643",
                    emphasis: {
                        focus: "series"
                    },
                    data: this.data.desalada
                }
            ]
        };
    }
}
</script>
