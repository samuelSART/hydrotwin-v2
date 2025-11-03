<template>
    <v-card tile :outlined="!dashboard" elevation="0">
        <template v-if="title">
            <v-card-title class="text-h6 font-heavy-light primary--text ma-5 pa-0">
                {{ title }}
            </v-card-title>
        </template>
        <div
            class="chart-content pa-5"
            :style="{ height: height, width: width }"
        ></div>
    </v-card>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from "vue-property-decorator";
import * as echarts from "echarts";

import { debounce } from "@/utils";

@Component
export default class OptionChart extends Vue {
    @Prop({ type: String, required: false, default: null })
    readonly title!: string;
    @Prop({ type: Boolean, required: false, default: false })
    readonly dashboard!: boolean;
    @Prop({ type: String, required: true }) readonly height!: boolean;
    @Prop({ type: String, default: "100%" }) readonly width!: string;
    @Prop({ type: Object, default: {} }) chartOptions!: object;

    @Watch("chartOptions", { immediate: true })
    onChartOptionsChanged() {
        /**
         * Check if DOM is ready, else initialize chart after next tick
         */
        if (this.$el) {
            this.initChart();
            return;
        }

        this.$nextTick(() => {
            this.initChart();
        });
    }

    chart!: echarts.ECharts | null;
    resizeHandler;

    mounted() {
        this.initResizeEvent();
    }

    beforeDestroy() {
        this.destroyResizeEvent();

        if (!this.chart) return;
        this.chart.dispose();
        this.chart = null;
    }

    initChart() {
        const container = this.$el.getElementsByClassName("chart-content")[0];
        if (!this.chart) {
            
            const theme = this.dashboard ?  "hydrotwin_dashboard" : "hydrotwin";
            this.chart = echarts.init(container as HTMLElement, theme );
        }
        this.setChartOptions(this.chartOptions);
    }

    setChartOptions(option = {}) {
        this.chart?.setOption(option, true);
    }

    initResizeEvent() {
        this.resizeHandler = debounce(() => {
            if (this.chart) {
                this.chart.resize();
            }
        }, 100);

        window.addEventListener("resize", this.resizeHandler);
    }

    clearChart() {
        if (!this.chart) return;
        this.chart.clear();
    }

    destroyResizeEvent() {
        window.removeEventListener("resize", this.resizeHandler);
    }
}
</script>

<style></style>
