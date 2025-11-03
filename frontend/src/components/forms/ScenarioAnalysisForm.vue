<template>
    <v-form ref="form">
        <v-row>
            <v-col v-if="optimizerForm">
                <v-subheader
                    >{{ $t("scenarioAnalysisForm.titleOptimization") }}
                </v-subheader>
                <v-subheader class="pl-2 ">
                    {{ $t("scenarioAnalysisForm.deficit") }}:
                    {{ formValues.waterDeficit }}
                </v-subheader>
                <v-slider
                    @change="changeWaterDeficit"
                    hide-details
                    thumb-label
                    v-model="formValues.waterDeficit"
                    max="100"
                    min="0"
                ></v-slider>

                <v-subheader class="pl-2 ">
                    {{ $t("scenarioAnalysisForm.co2") }}:
                    {{ formValues.CO2impact }}
                </v-subheader>
                <v-slider
                    @change="changeCO2impact"
                    hide-details
                    thumb-label
                    v-model="formValues.CO2impact"
                    max="100"
                    min="0"
                ></v-slider>
                <v-subheader class="pl-2 ">
                    {{ $t("scenarioAnalysisForm.hidroeconomic") }}:
                    {{ formValues.economicImpact }}
                </v-subheader>
                <v-slider
                    @change="changeEconomicImpact"
                    hide-details
                    thumb-label
                    v-model="formValues.economicImpact"
                    max="100"
                    min="0"
                ></v-slider>
            </v-col>
            <v-col>
                <v-subheader>{{
                    $t("scenarioAnalysisForm.titleWater")
                }}</v-subheader>
                <v-subheader class="pl-2 ">
                    {{ $t("scenarioAnalysisForm.superficial") }}:
                    {{
                        Math.round(
                            (formValues.superficial / 100) *
                                availableSources.superficial
                        )
                    }}
                    hm³
                </v-subheader>
                <v-slider
                    @change="computeWaterUsage"
                    hide-details
                    thumb-label
                    v-model="formValues.superficial"
                    max="150"
                    min="50"
                ></v-slider>
                <v-subheader class="pl-2">
                    {{ $t("scenarioAnalysisForm.subterranea") }}:
                    {{
                        Math.round(
                            (formValues.subterranea / 100) *
                                availableSources.subterranea
                        )
                    }}
                    hm³
                </v-subheader>
                <v-slider
                    @change="computeWaterUsage"
                    hide-details
                    thumb-label
                    v-model="formValues.subterranea"
                    max="150"
                    min="50"
                ></v-slider>
                <v-subheader class="pl-2">
                    {{ $t("scenarioAnalysisForm.reutilizada") }}:
                    {{
                        Math.round(
                            (formValues.reutilizada / 100) *
                                availableSources.reutilizada
                        )
                    }}
                    hm³
                </v-subheader>
                <v-slider
                    @change="computeWaterUsage"
                    hide-details
                    thumb-label
                    v-model="formValues.reutilizada"
                    max="150"
                    min="50"
                ></v-slider>
                <v-subheader class="pl-2">
                    {{ $t("scenarioAnalysisForm.trasvase") }}:
                    {{
                        Math.round(
                            (formValues.trasvase / 100) *
                                availableSources.trasvase
                        )
                    }}
                    hm³
                </v-subheader>
                <v-slider
                    @change="computeWaterUsage"
                    hide-details
                    thumb-label
                    v-model="formValues.trasvase"
                    max="150"
                    min="50"
                ></v-slider>
                <v-subheader class="pl-2">
                    {{ $t("scenarioAnalysisForm.desalada") }}:
                    {{
                        Math.round(
                            (formValues.desalada / 100) *
                                availableSources.desalada
                        )
                    }}
                    hm³
                </v-subheader>
                <v-slider
                    @change="computeWaterUsage"
                    hide-details
                    thumb-label
                    v-model="formValues.desalada"
                    max="150"
                    min="50"
                ></v-slider>
                <v-divider class="mx-0"></v-divider>
                <v-subheader
                    >{{ $t("scenarioAnalysisForm.waterUsage") }}
                    {{ totalWater }} hm³</v-subheader
                >
                <v-slider
                    hide-details
                    thumb-label
                    disabled
                    v-model="totalUsage"
                    max="150"
                    min="50"
                ></v-slider>
            </v-col>
        </v-row>
    </v-form>
</template>

<script lang="ts">
import { mapMutations } from "vuex";
import {
    Component,
    Vue,
    ModelSync,
    PropSync,
    Watch
} from "vue-property-decorator";
import {
    ScenarioAnalysisFormInterface,
    PlannerAvailableResources
} from "@/interfaces";
import * as types from "@/store/types";

@Component({
    methods: {
        ...mapMutations({
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class ScenarioAnalysisForm extends Vue {
    @ModelSync("ScenarioAnalysisForm", "change", { type: Object })
    formValues!: ScenarioAnalysisFormInterface;

    @PropSync("waterSources", { type: Object })
    availableSources!: PlannerAvailableResources;

    @PropSync("optimizer", { type: Boolean })
    optimizerForm!: boolean;

    totalWater = 0;
    totalUsage = 100;
    maxWater = 0;

    @Watch("availableSources.subterranea")
    async onDataChange() {
        this.maxWater =
            this.availableSources.subterranea +
            this.availableSources.superficial +
            this.availableSources.reutilizada +
            this.availableSources.desalada +
            this.availableSources.trasvase;
        this.computeWaterUsage();
    }

    computeWaterUsage() {
        this.maxWater =
            this.availableSources.subterranea +
            this.availableSources.superficial +
            this.availableSources.reutilizada +
            this.availableSources.desalada +
            this.availableSources.trasvase;
        this.totalWater = Math.floor(
            this.availableSources.subterranea *
                (this.formValues.subterranea / 100) +
                this.availableSources.superficial *
                    (this.formValues.superficial / 100) +
                this.availableSources.reutilizada *
                    (this.formValues.reutilizada / 100) +
                this.availableSources.desalada *
                    (this.formValues.desalada / 100) +
                this.availableSources.trasvase *
                    (this.formValues.trasvase / 100)
        );
        this.totalUsage = (this.totalWater / this.maxWater) * 100;
    }

    changeWaterDeficit() {
        const difference =
            this.formValues.waterDeficit +
            this.formValues.economicImpact +
            this.formValues.CO2impact -
            100;
        if (this.formValues.economicImpact == 0) {
            this.formValues.CO2impact -= difference;
        } else if (this.formValues.CO2impact == 0) {
            this.formValues.economicImpact -= difference;
        } else {
            const proportion = difference / 2;
            this.formValues.economicImpact -= proportion;
            this.formValues.CO2impact -= proportion;
            if (proportion % 1 != 0) {
                this.formValues.economicImpact +=
                    (proportion / proportion) * 0.5;
                this.formValues.CO2impact -= (proportion / proportion) * 0.5;
            }
        }
    }

    changeCO2impact() {
        const difference =
            this.formValues.waterDeficit +
            this.formValues.economicImpact +
            this.formValues.CO2impact -
            100;
        if (this.formValues.economicImpact == 0) {
            this.formValues.waterDeficit -= difference;
        } else if (this.formValues.waterDeficit == 0) {
            this.formValues.economicImpact -= difference;
        } else {
            const proportion = difference / 2;
            this.formValues.economicImpact -= proportion;
            this.formValues.waterDeficit -= proportion;
            if (proportion % 1 != 0) {
                this.formValues.waterDeficit += (proportion / proportion) * 0.5;
                this.formValues.economicImpact -=
                    (proportion / proportion) * 0.5;
            }
        }
    }

    changeEconomicImpact() {
        const difference =
            this.formValues.waterDeficit +
            this.formValues.economicImpact +
            this.formValues.CO2impact -
            100;
        if (this.formValues.CO2impact == 0) {
            this.formValues.waterDeficit -= difference;
        } else if (this.formValues.waterDeficit == 0) {
            this.formValues.CO2impact -= difference;
        } else {
            const proportion = difference / 2;
            this.formValues.waterDeficit -= proportion;
            this.formValues.CO2impact -= proportion;
            if (proportion % 1 != 0) {
                this.formValues.waterDeficit += (proportion / proportion) * 0.5;
                this.formValues.CO2impact -= (proportion / proportion) * 0.5;
            }
        }
    }
}
</script>
