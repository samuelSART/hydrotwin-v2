<template>
    <v-container fluid pa-0 ma-0>
        <div>
            <v-row>
                <v-col cols="8">
                    <v-breadcrumbs large divider=">" :items="items" />
                </v-col>
                <v-col cols="1">
                    <v-switch
                        v-model="planLength"
                        :disabled="loadingProgress != 0"
                        @change="switchUpdate"
                        :label="`${planLabel}`"
                    />
                </v-col>
                <v-col cols="1">
                    <v-checkbox
                        v-model="daily"
                        :disabled="!planLength || loadingProgress != 0"
                        @change="checkboxUpdate"
                        :label="$t('planner.daily')"
                    ></v-checkbox>
                </v-col>
                <v-col cols="1">
                    <v-btn
                        icon
                        prepend-icon="mdi-download"
                        @click="downloadCSV"
                    >
                        <v-icon>mdi-download</v-icon>
                    </v-btn>
                </v-col>
                <v-col cols="1">
                    <v-btn
                        class="ma-2"
                        outlined
                        small
                        fab
                        color="primary"
                        @click="openScenarioAnalysisDialog"
                    >
                        <v-icon>mdi-play</v-icon>
                    </v-btn>
                </v-col>
            </v-row>
            <v-row>
                <PlanConfiguration ref="chartPlanConfig" :planData="planData" />
            </v-row>
            <v-row class="ma-2 mb-0">
                <v-skeleton-loader
                    v-if="skeleton"
                    boilerplate
                    height="200px"
                    width="100%"
                    type="image"
                ></v-skeleton-loader>
                <v-col v-if="!skeleton">
                    <WaterDeficitChart
                        ref="chartDeficit"
                        :plotData="plotData"
                    />
                </v-col>
                <v-col v-if="!skeleton">
                    <CO2EmissionChart
                        ref="chartEmission"
                        :plotData="plotData"
                    />
                </v-col>
                <v-col v-if="!skeleton">
                    <HidroEconomicChart
                        ref="chartEconomic"
                        :plotData="plotData"
                    />
                </v-col>
                <v-col v-if="!skeleton">
                    <SourceDistributionChart
                        ref="chartSources"
                        :plotData="plotData"
                    />
                </v-col>
            </v-row>
            <v-row class="ml-5 mr-5 mt-0" style="margin-bottom:64px;">
                <v-col>
                    <PlannerTable
                        v-if="!hiddeTable"
                        ref="plannerTable"
                        :tableData="tableData"
                        line="l5"
                /></v-col>
            </v-row>
        </div>
        <ScenarioAnalysisDiaolog
            v-model="dialog"
            :planLength="planLength"
            :planDaily="daily"
            :optimizer="true"
            @plan-generator-running="optimizerRuning"
        />
    </v-container>
</template>

<script lang="ts">
import { Vue, Component, Ref, Watch } from "vue-property-decorator";
import { mapMutations } from "vuex";
import { Dictionary } from "vue-router/types/router";

import { Timer } from "@/utils/Timer";
import WaterDeficitChart from "@/pages/components/charts/waterDeficitChart.vue";
import SourceDistributionChart from "@/pages/components/charts/sourceDistributionChart.vue";
import CO2EmissionChart from "@/pages/components/charts/CO2EmissionChart.vue";
import HidroEconomicChart from "@/pages/components/charts/hidroEconomicChart.vue";
import PlanConfiguration from "@/pages/components/charts/planConfiguration.vue";
import PlannerTable from "@/pages/components/tables/plannerTable.vue";
import {
    OptimizerPlotData,
    OptimizerPlotDataResponse,
    PlannerTableData,
    PlannerTableDataResponse,
    PlannerConfigData,
    PlannerConfigDataResponse,
    ResponseDownloadData
} from "@/interfaces";
import * as types from "@/store/types";

@Component({
    components: {
        WaterDeficitChart: () =>
            import("@/pages/components/charts/waterDeficitChart.vue"),
        SourceDistributionChart: () =>
            import("@/pages/components/charts/sourceDistributionChart.vue"),
        CO2EmissionChart: () =>
            import("@/pages/components/charts/CO2EmissionChart.vue"),
        HidroEconomicChart: () =>
            import("@/pages/components/charts/hidroEconomicChart.vue"),
        PlannerTable: () =>
            import("@/pages/components/tables/plannerTable.vue"),
        ScenarioAnalysisDiaolog: () =>
            import("@/components/dialogs/ScenarioAnalysisDialog.vue"),
        ScenarioAnalysisForm: () =>
            import("@/components/forms/ScenarioAnalysisForm.vue"),
        PlanConfiguration: () =>
            import("@/pages/components/charts/planConfiguration.vue")
    },
    methods: {
        ...mapMutations({
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE,
            setProgressBar: types.MUTATE_APP_PROGRESSBAR
        })
    }
})
export default class Planner extends Vue {
    @Ref("chartDeficit") readonly chartDeficit!: WaterDeficitChart;
    @Ref("chartSources") readonly chartSources!: SourceDistributionChart;
    @Ref("chartEmission") readonly chartEmission!: CO2EmissionChart;
    @Ref("chartEconomic") readonly chartEconomic!: HidroEconomicChart;
    @Ref("chartPlanConf") readonly chartPlanConf!: PlanConfiguration;
    @Ref("plannerTable") readonly plannerTable!: PlannerTable;

    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;
    setProgressBar!: (state: boolean) => void;

    items: Dictionary<string>[] = [
        {
            text: "Murcia",
            href: "#/l5/dashboard"
        }
    ];

    selectedCategory: string | undefined = "";
    selectedUD: string | undefined = "";
    hiddeTable = false;
    dialog = false;
    daily = true;
    planLength = false;
    planLabel = this.$t("planner.shortplan");
    loadingProgress = 0;
    timer!: Timer;

    skeleton = true;

    plotData: OptimizerPlotData = {
        date: [],
        demand: [],
        planned: [],
        incertLow: [],
        incertHigh: [],
        superficial: [],
        subterranea: [],
        reutilizada: [],
        trasvase: [],
        desalada: [],
        CO2: [],
        economic: [],
        oldPlan: undefined
    };

    tableData: PlannerTableData[] = [];

    planData: PlannerConfigData = {
        CO2impact: 0,
        waterDeficit: 0,
        economicImpact: 0,
        superficial: 0,
        subterranea: 0,
        reutilizada: 0,
        trasvase: 0,
        desalada: 0,
        start: "",
        end: "",
        creationDate: ""
    };

    @Watch("$route.params")
    async onRouteUpdate() {
        this.clearData();
        this.updateData();
    }

    mounted() {
        this.updateData();
        this.timer = new Timer({
            timeout: 20000,
            immediate: true
        });
        this.timer.on("tick", async () => {
            this.checkOptimizedPlanGenerated();
        });
        const planId = localStorage.getItem("plannerRuning");
        if (planId != undefined) {
            this.timer.start();
        }
    }

    destroyed() {
        this.timer.stop();
    }

    updateData() {
        this.selectedCategory = this.$route.params.type;
        this.selectedUD = this.$route.params.ud;
        this.hiddeTable =
            this.selectedCategory != undefined && this.selectedUD != undefined;
        this.fetchPlotOptimizerData();
        if (!this.hiddeTable) {
            this.fetchTableData();
        }
        this.fetchPlanConfigData();
        this.updateBreadcrumbs();
    }

    fetchPlotOptimizerData() {
        this.skeleton = true;
        this.setProgressBar(true);
        this.loadingProgress += 1;
        this.$api
            .getOptimizerPlotData<OptimizerPlotDataResponse>(
                this.selectedCategory,
                this.selectedUD,
                this.planLength,
                this.daily
            )
            .then(response => {
                if (response.status == 200) {
                    this.skeleton = false;
                    this.plotData = response.data;
                    this.loadingProgress -= 1;
                    if (this.loadingProgress == 0) this.setProgressBar(false);
                }
                if (response.status == 202) {
                    this.loadingProgress = 0;
                    this.setProgressBar(false);
                    this.showMsg(String(this.$t("optimizer.noPlan")));
                }
            })
            .catch(error => {
                if (error instanceof Error) {
                    this.skeleton = true;
                    this.loadingProgress -= 1;
                    if (this.loadingProgress == 0) this.setProgressBar(false);
                    this.showMsg(`${this.$t("netError")}`);
                    this.clearPlotData();
                }
            });
    }

    fetchTableData() {
        this.setProgressBar(true);
        this.loadingProgress += 1;
        this.$api
            .getOptimizerTableData<PlannerTableDataResponse>(
                this.selectedCategory,
                this.planLength,
                this.daily
            )
            .then(response => {
                if (response.status == 200) {
                    this.tableData = response.data;
                    this.loadingProgress -= 1;
                    if (this.loadingProgress == 0) this.setProgressBar(false);
                }
                if (response.status == 202) {
                    this.loadingProgress = 0;
                    this.setProgressBar(false);
                    this.showMsg(String(this.$t("planner.noPlan")));
                }
            })
            .catch(error => {
                if (error instanceof Error) {
                    this.loadingProgress -= 1;
                    if (this.loadingProgress == 0) this.setProgressBar(false);
                    this.showMsg(`${this.$t("netError")}`);
                    this.tableData = [];
                }
            });
    }

    fetchPlanConfigData() {
        this.setProgressBar(true);
        this.loadingProgress += 1;
        this.$api
            .getOptimizedPlanConfigData<PlannerConfigDataResponse>(
                this.planLength,
                this.daily
            )
            .then(response => {
                if (response.status == 200) {
                    this.planData = response.data;
                    this.loadingProgress -= 1;
                    if (this.loadingProgress == 0) this.setProgressBar(false);
                }
                if (response.status == 202) {
                    this.loadingProgress = 0;
                    this.setProgressBar(false);
                    this.showMsg(String(this.$t("planner.noPlan")));
                }
            })
            .catch(error => {
                if (error instanceof Error) {
                    this.loadingProgress -= 1;
                    if (this.loadingProgress == 0) this.setProgressBar(false);
                    this.showMsg(`${this.$t("netError")}`);
                    this.planData = {
                        CO2impact: 0,
                        waterDeficit: 0,
                        economicImpact: 0,
                        superficial: 0,
                        subterranea: 0,
                        reutilizada: 0,
                        trasvase: 0,
                        desalada: 0,
                        start: "",
                        end: "",
                        creationDate: ""
                    };
                }
            });
    }

    updateBreadcrumbs() {
        this.items = [
            {
                text: "Murcia",
                href: "#/l5/dashboard"
            }
        ];
        if (this.selectedCategory) {
            this.items.push({
                text: this.selectedCategory,
                href: `#/l5/dashboard/${this.selectedCategory}`
            });
        }
        if (this.selectedUD) {
            this.items.push({
                text: this.selectedUD,
                href: `#/l5/dashboard/${this.selectedCategory}/${this.selectedUD}`
            });
        }
    }

    optimizerRuning(hash: string) {
        localStorage.setItem("optimizerRuning", hash);
        this.timer.start();
    }

    checkOptimizedPlanGenerated() {
        const planId = localStorage.getItem("optimizerRuning");
        if (planId == undefined) {
            this.timer.stop();
            return;
        }
        this.$api
            .checkOptimizedPlanGenerated<Response>(planId)
            .then(response => {
                if (response.status == 200) {
                    this.showMsg(String(this.$t("optimizer.planGenerated")));
                    localStorage.removeItem("optimizerRuning");
                    this.updateData();
                }
            })
            .catch(error => {
                if (error instanceof Error) {
                    this.showMsg(`${this.$t("netError")}`);
                    localStorage.removeItem("optimizerRuning");
                }
            });
    }

    clearPlotData() {
        this.plotData = {
            date: [],
            demand: [],
            planned: [],
            incertLow: [],
            incertHigh: [],
            superficial: [],
            subterranea: [],
            reutilizada: [],
            trasvase: [],
            desalada: [],
            CO2: [],
            economic: [],
            oldPlan: undefined
        };
    }

    clearData() {
        this.loadingProgress = 0;
        this.setProgressBar(false);
        this.clearPlotData();
        this.planData = {
            CO2impact: 0,
            waterDeficit: 0,
            economicImpact: 0,
            superficial: 0,
            subterranea: 0,
            reutilizada: 0,
            trasvase: 0,
            desalada: 0,
            start: "",
            end: "",
            creationDate: ""
        };
        this.tableData = [];
    }

    showMsg(msg: string) {
        this.setInfoMessage({ shown: true, text: msg });
    }

    openScenarioAnalysisDialog() {
        const planId = localStorage.getItem("optimizerRuning");
        if (planId != undefined) {
            this.showMsg(String(this.$t("optimizer.planGenerating")));
            return;
        }
        this.dialog = true;
    }

    switchUpdate() {
        if (this.planLength == false) {
            this.planLabel = this.$t("planner.shortplan");
            this.daily = true;
        } else {
            this.planLabel = this.$t("planner.longplan");
            this.daily = false;
        }
        this.clearData();
        this.updateData();
    }

    checkboxUpdate() {
        if (this.planLength) {
            this.clearData();
            this.updateData();
        }
    }

    async downloadCSV() {
        const response = await this.$api.downloadOptimizerData<
            ResponseDownloadData
        >(this.planLength, this.daily);
        if (!response) return;
        if (response.status == 204) {
            this.showMsg(String(this.$t("NoDataToDownload")));
            return;
        }
        let planType = "short";
        if (this.planLength) {
            planType = "long";
        }
        let step = "daily";
        if (this.planLength && this.daily == false) {
            step = "monthly";
        }
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute(
            "download",
            `optimized_plan_${planType}_term_${step}_step.csv`
        );
        document.body.appendChild(link);
        link.click();
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
<style lang="scss">
.centered-input input {
    text-align: center;
}
</style>
