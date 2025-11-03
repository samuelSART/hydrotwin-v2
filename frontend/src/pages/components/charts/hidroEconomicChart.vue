<template>
    <OptionChart
        ref="chart"
        height="400px"
        dashboard
        :chart-options="economicChartOptions"
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
export default class HidroEconomicChart extends Vue {
    @Ref("chart") readonly chartEconomic!: OptionChart;
    economicChartOptions: EChartsOption = {};

    @PropSync("plotData", { type: Object })
    data!: OptimizerPlotData;

    @Watch("data.date")
    async onDataChange() {
        this.clearChart();
        if (this.data.date.length > 0) {
            this.loadHidroEconomic();
        }
    }

    mounted() {
        this.clearChart();
        if(this.data != undefined){
            if (this.data.date.length > 0) {
                this.loadHidroEconomic();
            }
        }
    }

    /**
     * Clear chart
     * @return {void}
     */
    clearChart(): void {
        if (!this.chartEconomic) return;
        this.chartEconomic.clearChart();
    }

    loadHidroEconomic(): void {
        this.economicChartOptions = {
            title: {
                text: String(this.$t("hidroeconomicChart.chartTitle")),
                left: "center"
            },
            tooltip: {
                trigger: "axis",
                formatter: (params: any) => {
                    let result = `${params[0].name} <br>`;
                    params.forEach((param: any) => {
                        result += `${param.marker} ${param.seriesName}: ${(param.value / 1000).toFixed(2)} K€<br/>`;
                    });
                    return result;
                }
            },
            
            legend: {
                data:
                    this.data?.oldPlan != undefined
                        ? [String(this.$t("hidroeconomicChart.planned")), String(this.$t("hidroeconomicChart.nonOptimized"))]
                        : [],
                left: 10,
                top: 30
            },
            grid: {
                    left: "15%",
                },
            xAxis: {
                type: "category",
                boundaryGap: false,
                data: this.data.date
            },
            yAxis: [
                {
                    type: "value",
                    position: "left",
                    axisLine: {
                        show: false
                    },
                    axisLabel: {
                        formatter: (value) => {
                            return (value / 1000).toExponential() + "";
                        } 
                    },
                    axisPointer: {
                        snap: false
                    }
                }
            ],
            series: [
                {
                    name: String(this.$t("hidroeconomicChart.planned")),
                    type: "line",
                    smooth: true,
                    data: this.data.economic
                },
                {
                    name: String(this.$t("hidroeconomicChart.nonOptimized")),
                    type: "line",
                    color: "grey",
                    smooth: true,
                    data:
                        this.data?.oldPlan != undefined
                            ? this.data.oldPlan?.economic
                            : []
                }
            ]
        };
    }
}
</script>
