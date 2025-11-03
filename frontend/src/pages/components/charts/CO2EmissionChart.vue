<template>
    <OptionChart
        ref="chart"
        height="400px"
        dashboard
        :chart-options="co2EmissionChartOption"
    />
</template>

<script lang="ts">
import { Vue, Component, Ref, PropSync, Watch } from "vue-property-decorator";
import { EChartsOption } from "echarts";
import OptionChart from "@/components/charts/OptionChart.vue";
import { OptimizerPlotData } from "@/interfaces";
@Component({
    components: {
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    }
})
export default class CO2EmissionChart extends Vue {
    @Ref("chart") readonly chartEmission!: OptionChart;
    co2EmissionChartOption: EChartsOption = {};

    @PropSync("plotData", { type: Object })
    data!: OptimizerPlotData;

    @Watch("data.date")
    async onDataChange() {
        this.clearChart();
        if (this.data.date.length > 0) {
            this.loadEmissionChart();
        }
    }

    mounted() {
        this.clearChart();
        if (this.data != undefined) {
            if (this.data.date.length > 0) {
                this.loadEmissionChart();
            }
        }
    }

    /**
     * Clear chart
     * @return {void}
     */
    clearChart(): void {
        if (!this.chartEmission) return;
        this.chartEmission.clearChart();
    }

    loadEmissionChart(): void {
        this.co2EmissionChartOption = {
            title: {
                text: String(this.$t("CO2EmissionsChart.chartTitle")),
                left: "center"
            },
            tooltip: {
                trigger: "axis",
                formatter: (params: any) => {
                    let result = `${params[0].name} <br>`;
                    params.forEach((param: any) => {
                        result += `${param.marker} ${param.seriesName}: ${(param.value).toFixed(0) } t CO<sub>2</sub> <br/>`;
                    });
                    return result;
                }
            },
            legend: {
                data:
                    this.data?.oldPlan != undefined
                        ? [String(this.$t("CO2EmissionsChart.planned")), String(this.$t("CO2EmissionsChart.nonOptimized"))]
                        : [],
                left: 10,
                top: 30
            },
            grid: {
                    left: "15%",
                },
            xAxis: {
                type: "category",
                // prettier-ignore
                data: this.data.date
            },
            yAxis: {
                type: "value",
                position: "left",
                axisLabel: {
                    formatter: (value) => {
                        return value.toExponential()  + "";
                    }
                }
            },
            series: [
                {
                    name: String(this.$t("CO2EmissionsChart.planned")),
                    type: "line",
                    smooth: true,
                    // prettier-ignore
                    data: this.data.CO2
                },
                {
                    name: String(this.$t("CO2EmissionsChart.nonOptimized")),
                    type: "line",
                    color: "grey",
                    smooth: true,
                    step: "end",
                    data:
                        this.data?.oldPlan != undefined
                            ? this.data.oldPlan?.CO2
                            : []
                }
            ]
        };
    }
}
</script>
