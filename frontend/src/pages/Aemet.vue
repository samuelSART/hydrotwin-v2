<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <v-tabs centered>
                <v-tab>{{ $t("aemet.currentWeather") }}</v-tab>
                <v-tab>{{ $t("aemet.searchByDates") }}</v-tab>
                <v-tab-item><CurrentWeather /></v-tab-item>
                <v-tab-item><RangeWeather /></v-tab-item>
            </v-tabs>
        </div>
    </v-container>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";

@Component({
    components: {
        CurrentWeather: () =>
            import("@/pages/components/aemet/CurrentWeather.vue"),
        RangeWeather: () => import("@/pages/components/aemet/RangeWeather.vue")
    }
})
export default class Aemet extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

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

<style lang="scss" scoped>
.wrap {
    height: 90%;
    height: calc(100vh - 128px);
    width: 100%;
}
</style>
<style></style>
