<template>
    <div class="wrap my-5">
        <v-tabs centered>
            <v-tab>{{ $t("aemet.table") }}</v-tab>
            <v-tab>{{ $t("aemet.chart") }}</v-tab>
            <v-tab-item><WeatherTable /></v-tab-item>
            <v-tab-item><WeatherChart /></v-tab-item>
        </v-tabs>
    </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component({
    components: {
        WeatherTable: () => import("@/pages/components/aemet/WeatherTable.vue"),
        WeatherChart: () => import("@/pages/components/aemet/WeatherChart.vue")
    }
})
export default class RangeWeather extends Vue {}
</script>

<style lang="scss" scoped>
.wrap {
    height: 90%;
    height: calc(100vh - 152px);
    width: 100%;
}
</style>
<style></style>
