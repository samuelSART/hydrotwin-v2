<template>
    <v-card v-if="show">
        <OptionChart
            ref="chart"
            height="400px"
            dashboard
            :chart-options="variableOption"
        />
    </v-card>
</template>

<script lang="ts">
import { EChartsOption, SeriesOption } from "echarts";
import { Component, Vue, PropSync, Watch, Ref } from "vue-property-decorator";
import { Feature } from "geojson";
//import moment from "moment";

import {
    WMSFilterFormInterface,
    VariableValue,
    VariableValueResponse as vvr
} from "@/interfaces";

import OptionChart from "@/components/charts/OptionChart.vue";

@Component({
    components: {
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    }
})
export default class WMSchart extends Vue {
    @PropSync("WMSFilterForm", { type: Object })
    filterForm!: WMSFilterFormInterface;

    @Ref("chart") readonly chart!: OptionChart;

    variableOption: EChartsOption = {};

    show = false;
    geometryList: Feature[] = [];
    geometryNames: string[] = [];
    geometrySeries: SeriesOption[] = [];


    @Watch("filterForm.style")
    async onStyleUpdate() {
        this.filterForm.valid ? this.reloadChart() : this.clearChart();
    }

    @Watch("filterForm.selectedDate")
    async onDateUpdate() {
        this.filterForm.valid ? this.reloadChart() : this.clearChart();
    }

    deleteAll(){
        this.geometryList = [];
        this.geometryNames = [];
        this.geometrySeries = [];
        this.clearChart();
    }

    async reloadChart() {
        const tempGeometryList = this.geometryList;
        this.geometryList = [];
        this.geometryNames = [];
        this.geometrySeries = [];
        this.clearChart();
        for (let i = 0; i < tempGeometryList.length; i++)
            this.onCreatePolygon(tempGeometryList[i]);
    }

    async onCreatePolygon(feature) {
        await this.loadNewFeatureData(feature);
        this.createPlot();
    }

    async onUpdatePolygon(feature) {
        this.onDeletePolygon(feature.properties.description);
        await this.onCreatePolygon(feature);
    }

    async onDeletePolygon(featureId) {
        if (featureId == undefined){
            return;
        }
        const index = this.geometryNames.indexOf(featureId);
        this.geometryNames.splice(index, 1);
        this.geometryList.splice(index, 1);
        this.geometrySeries.splice(index, 1);
        if (this.geometryNames.length == 0) {
            this.clearChart();
        } else {
            this.createPlot();
        }
    }

    /**
     * Clear chart
     * @return {void}
     */
    clearChart(): void {
        if (!this.chart) return;
        this.show = false;
        this.chart.clearChart();
    }

    /**
     * Load variable data
     *
     */
    async getPredictionGeometryStats(
        feature
    ): Promise<VariableValue[] | undefined> {
        const layer = this.filterForm.layer.layer;
        const style = this.filterForm.style.style;
        const startDate = this.filterForm.selectedDate;
        const endDate = new Date(new Date().setDate(new Date().getDate() + 210))
            .toISOString()
            .split("T")[0];
        const geometryStats = await this.$api.getWMSGeometryStats<vvr>(
            layer,
            style,
            startDate,
            endDate,
            feature?.geometry
        );
        return geometryStats.data;
    }

    /**
     * Load new feature data
     *
     */
    async loadNewFeatureData(feature) {
        const variableValues:
            | VariableValue[]
            | undefined = await this.getPredictionGeometryStats(feature);

        const newSerie = feature.properties?.description;
        /**
         * Data as arrays of [{timestamp}, {value}]
         */
        const data = variableValues?.map(({ _time, _value }: VariableValue) => [
            +new Date(_time),
            _value
        ]);
        this.geometryNames.push(newSerie);
        this.geometryList.push(feature);
        this.geometrySeries.push({
            name: newSerie,
            data: data,
            smooth: true,
            type: "line",
            stack: "Geometry",
            animationDuration: 700,
            animationEasing: "quadraticOut"
        });
    }

    /**
     * Plot variable data
     * @return {Promise<void>}
     */
    async createPlot(): Promise<void> {
        if (this.geometryNames.length != 0) {
            this.show = true;

            this.variableOption = {
                xAxis: {
                    type: "time",
                    axisTick: {
                        show: true
                    }
                },
                legend: {
                    textStyle: {
                        fontWeight: "bold"
                    }
                },
                grid: {
                    left: "3%",
                    right: "4%",
                    bottom: "3%",
                    containLabel: true
                },
                tooltip: {
                    trigger: "axis"
                },
                toolbox: {
                    feature: {
                        dataZoom: {
                            yAxisIndex: "none"
                        },
                        restore: {}
                    }
                },
                yAxis: {
                    axisTick: {
                        show: true
                    },
                    type: "value"
                },
                series: this.geometrySeries
            };
        }
    }
}
</script>
