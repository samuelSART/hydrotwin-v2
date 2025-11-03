<template>
    <BaseDialog
        v-model="dialogShown"
        :loading="loading"
        :title="$t('scenarioAnalysisDialog.title')"
    >
        <template #plot class="mx-0 px-0">
            <ScenarioAnalysisForm
                v-model="scenarioForm"
                :optimizer="optimizerForm"
                :waterSources="availableSources"
            />
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="black darken-1" text @click="dialogShown = false">
                    {{ $t("scenarioAnalysisDialog.cancel") }}
                </v-btn>
                <v-btn color="green darken-1" text @click="generatePlan">
                    {{ $t("scenarioAnalysisDialog.run") }}
                </v-btn>
            </v-card-actions>
        </template>
    </BaseDialog>
</template>

<script lang="ts">
import {
    Component,
    Vue,
    ModelSync,
    PropSync,
    Watch
} from "vue-property-decorator";
import * as types from "@/store/types";
import { mapMutations } from "vuex";
import {
    ScenarioAnalysisFormInterface,
    PlannerAvailableResourcesResponse,
    PlannerAvailableResources,
    ScenarioAnalysisExecutionResponse
} from "@/interfaces";

@Component({
    components: {
        BaseDialog: () => import("@/components/dialogs/BaseDialog.vue"),
        ScenarioAnalysisForm: () =>
            import("@/components/forms/ScenarioAnalysisForm.vue")
    },
    methods: {
        ...mapMutations({
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class ScenarioAnalysisDiaolog extends Vue {
    @ModelSync("dialogShownValue", "change", { type: Boolean })
    dialogShown!: boolean;

    @PropSync("planLength", { type: Boolean })
    monthly!: boolean;

    @PropSync("planDaily", { type: Boolean })
    daily!: boolean;

    @PropSync("optimizer", { type: Boolean })
    optimizerForm!: boolean;

    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    loading = true;

    scenarioForm: ScenarioAnalysisFormInterface = {
        subterranea: 100,
        superficial: 100,
        reutilizada: 100,
        desalada: 100,
        trasvase: 100,
        waterDeficit: 34,
        CO2impact: 33,
        economicImpact: 33,
        valid: true
    };

    availableSources: PlannerAvailableResources = {
        subterranea: 0,
        superficial: 0,
        reutilizada: 0,
        desalada: 0,
        trasvase: 0
    };

    availableSourceList: PlannerAvailableResources[] = [];

    @Watch("monthly")
    onPlanLengthChange() {
        if (this.monthly) {
            this.availableSources = this.availableSourceList[1];
        } else {
            this.availableSources = this.availableSourceList[0];
        }
    }

    mounted() {
        this.fecthAvailableResources();
    }

    fecthAvailableResources() {
        this.$api
            .getAvailableResources<PlannerAvailableResourcesResponse>()
            .then(response => {
                if (response.ok) {
                    this.availableSourceList = response.data;
                    if (this.monthly) {
                        this.availableSources = this.availableSourceList[1];
                    } else {
                        this.availableSources = this.availableSourceList[0];
                    }
                    this.loading = false;
                }
            })
            .catch(error => {
                if (error instanceof Error) {
                    this.dialogShown = false;
                    this.showError(`${this.$t("netError")}`);
                }
            });
    }

    generatePlan() {
        this.$api
            .generatePlan<ScenarioAnalysisExecutionResponse>(
                this.monthly,
                this.daily,
                this.scenarioForm,
                this.optimizerForm
            )
            .then(response => {
                if (response.ok) {
                    this.dialogShown = false;
                    this.setInfoMessage({
                        shown: true,
                        text: String(this.$t("scenarioAnalysisDialog.generating"))
                    });
                    this.dialogShown = false;
                    this.$emit("plan-generator-running", response.data);
                }
            })
            .catch(error => {
                if (error instanceof Error) {
                    this.dialogShown = false;
                    this.showError(`${this.$t("netError")}`);
                }
            });
    }

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>
