<template>
    <v-row class="ma-2 mb-0 mt-0">
        <v-col>
            <v-skeleton-loader
                v-if="skeleton"
                boilerplate
                type="image"
            ></v-skeleton-loader>
            <v-card v-if="!skeleton" color="primary">
                <v-card-text>
                    <div class="text-h6 font-heavy-light white--text mb-3">
                        {{ $t("planConfiguration.chartTitle") }}
                    </div>
                    <div class="subheading font-weight-light grey--text">
                        {{ $t("planConfiguration.start") }} <br />
                        {{ data.start }}
                    </div>
                    <div class="subheading font-weight-light grey--text">
                        {{ $t("planConfiguration.end") }} <br />{{ data.end }}
                    </div>
                    <v-divider ligth class="my-2"></v-divider>
                    <v-icon class="mr-2" color="white" small>
                        mdi-clock
                    </v-icon>
                    <span class="text-caption grey--text font-weight-light"
                        >{{ $t("planConfiguration.generated") }} {{ data.creationDate }}</span
                    >
                </v-card-text>
            </v-card>
        </v-col>
        <v-col>
            <v-skeleton-loader
                v-if="skeleton"
                boilerplate
                type="image"
            ></v-skeleton-loader>
            <v-card v-if="!skeleton" color="primary">
                <v-card-text>
                    <div class="text-h6 font-weight-heavy white--text mt-0">
                        {{ $t("planConfiguration.waterUse") }} 
                    </div>
                    <v-divider class="my-1"></v-divider>
                    <div class="subheading font-weight-light grey--text">
                        {{ $t("planner.superficial") }}  ( {{ (data.superficial * 100).toFixed(4)}} % )
                        <v-progress-linear
                            :value="(data.superficial * 100) / 1.5"
                            color="#893448"
                        />
                        {{ $t("planner.subterranea") }}  ( {{ (data.subterranea * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="(data.subterranea * 100) / 1.5"
                            color="#d95850"
                        />
                        {{ $t("planner.reutilizada") }}  ( {{ (data.reutilizada * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="(data.reutilizada * 100) / 1.5"
                            color="#eb8146"
                        />
                        {{ $t("planner.trasvase") }}  ( {{ (data.trasvase * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="(data.trasvase * 100) / 1.5"
                            color="#ffb248"
                        />
                        {{ $t("planner.desalada") }}  ( {{ (data.desalada * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="(data.desalada * 100) / 1.5"
                            color="#f2d643"
                        />
                    </div>
                </v-card-text>
            </v-card>
        </v-col>
        <v-col>
            <v-skeleton-loader
                v-if="skeleton"
                boilerplate
                type="image"
            ></v-skeleton-loader>
            <v-card v-if="!skeleton" color="primary">
                <v-card-text>
                    <div class="text-h6 font-weight-heavy white--text mb-2">
                        {{ $t("planConfiguration.impactImportance") }} 
                    </div> 
                    <v-divider class="my-2"></v-divider>
                    <div class="subheading font-weight-light grey--text">
                        {{ $t("planConfiguration.deficit") }}  ( {{ (data.waterDeficit * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="data.waterDeficit * 100 "
                            color="cyan"
                        /><br />
                        {{ $t("planConfiguration.co2") }}  ( {{ (data.CO2impact * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="data.CO2impact * 100"
                            color="amber"
                        /><br />
                        {{ $t("planConfiguration.hidroeconomic") }}  ( {{ (data.economicImpact * 100).toFixed(4) }} % )
                        <v-progress-linear
                            :value="data.economicImpact * 100"
                            color="green"
                        />
                    </div>
                </v-card-text>
            </v-card>
        </v-col>
    </v-row>
</template>

<script lang="ts">
import { Vue, Component, PropSync, Watch } from "vue-property-decorator";

import { PlannerConfigData } from "@/interfaces";

@Component({
    components: {
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    }
})
export default class PlanConfiguration extends Vue {
    @PropSync("planData", { type: Object })
    data!: PlannerConfigData;

    skeleton = false;

    @Watch("data.creationDate")
    async onDataChange() {
        if (this.data.creationDate != "") {
            this.skeleton = false;
            return;
        }
        this.skeleton = true;
    }

    mounted() {
        if (this.data.creationDate != "") {
            this.skeleton = false;
            return;
        }
        this.skeleton = true;
    }
}
</script>

<style>
.v-sheet--offset {
    top: -10px;
    position: relative;
}
.theme--light.v-divider {
    border-color: rgba(255, 255, 255, 0.705) !important;
}
</style>
