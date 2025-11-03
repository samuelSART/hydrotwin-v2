<template>
    <div class="wrap">
        <v-tabs centered>
            <v-tab>{{ this.$t("droughtIndices.maps") }}</v-tab>
            <v-tab>{{ this.$t("droughtIndices.charts") }}</v-tab>
            <v-tab>{{ this.$t("droughtIndices.tables") }}</v-tab>
            <v-tab-item><DroughtMaps /></v-tab-item>
            <v-tab-item><DroughtCharts /></v-tab-item>
            <v-tab-item><DroughtTables /></v-tab-item>
        </v-tabs>
    </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component({
    components: {
        DroughtCharts: () =>
            import("@/pages/components/droughtIndices/DroughtCharts.vue"),
        DroughtTables: () =>
            import("@/pages/components/droughtIndices/DroughtTables.vue"),
        DroughtMaps: () =>
            import("@/pages/components/droughtIndices/DroughtMaps.vue")
    }
})
export default class DroughtIndices extends Vue {}
</script>

<style lang="scss" scoped>
.wrap {
    height: 90%;
    height: calc(100vh - 128px);
    width: 100%;
}
</style>
<style></style>
