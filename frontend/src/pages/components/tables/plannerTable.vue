<template>
    <v-card>
        <v-skeleton-loader
            v-if="skeleton"
            height="400px"
            boilerplate
            type="table-thead,table-tbody"
        ></v-skeleton-loader>
        <v-data-table
            v-if="!skeleton"
            :items-per-page="5"
            :headers="headers"
            :items="data"
            item-key="name"
            color="primary"
            class="elevation-0"
        >
            <template v-slot:[`item.name`]="{ item }">
                <router-link :to="item.route">{{ item.name }}</router-link>
            </template>
            <template v-slot:[`item.deficitPerDay`]="{ item }">
                <v-tooltip
                    bottom
                    v-for="(values, i) in item.deficitPerDay"
                    :key="i"
                >
                    <template v-slot:activator="{ on, attrs }">
                        <v-icon
                            medium
                            v-bind="attrs"
                            v-on="on"
                            :color="valueColor(values)"
                            >mdi-checkbox-blank</v-icon
                        >
                    </template>
                    <span v-text="tooltipText(values, i)"></span>
                </v-tooltip>
            </template>
        </v-data-table>
    </v-card>
</template>

<script lang="ts">
import { Vue, Component, PropSync, Watch } from "vue-property-decorator";
import { Dictionary } from "vue-router/types/router";
import { PlannerTableData } from "@/interfaces";
@Component
export default class PlannerTable extends Vue {
    @PropSync("tableData", { type: Array })
    data!: PlannerTableData[];

    @PropSync("line", { type: String })
    routeLine!: string;

    skeleton = false;

    headers: Dictionary<string | boolean>[] = [
        {
            text: String(this.$t("plannerTable.name")),
            align: "start",
            value: "name"
        },
        { text: String(this.$t("plannerTable.demanda")), value: "demand" },
        { text: String(this.$t("plannerTable.flow")), value: "planned" },
        { text: String(this.$t("plannerTable.deficit")), value: "deficit" },
        { text: String(this.$t("plannerTable.co2")), value: "emission" },
        { text: String(this.$t("plannerTable.income")), value: "economical" },
        {
            text: String(this.$t("plannerTable.superfical")),
            value: "superficial"
        },
        {
            text: String(this.$t("plannerTable.subterranea")),
            value: "subterranea"
        },
        {
            text: String(this.$t("plannerTable.reutilizada")),
            value: "reutilizada"
        },
        { text: String(this.$t("plannerTable.trasvase")), value: "trasvase" },
        { text: String(this.$t("plannerTable.desalada")), value: "desalada" },
        {
            text: String(this.$t("plannerTable.deficitPerDay")),
            value: "deficitPerDay",
            sortable: false
        }
    ];

    @Watch("data")
    async onDataChange() {
        if (this.data.length > 0) {
            this.loadTableData();
            this.skeleton = false;
            return;
        }
        this.skeleton = true;
    }
    selectedCategory: string | undefined = "";

    @Watch("$route.params")
    async onRouteUpdate() {
        this.selectedCategory = this.$route.params.type;
    }

    mounted() {
        if (this.data.length > 0) {
            this.loadTableData();
            this.skeleton = false;
            return;
        }
        this.skeleton = true;
    }
    valueColor(value) {
        return 0 > value ? "red" : "green";
    }

    tooltipText(value, i) {
        return `${this.data[0].dates[i]}: ${value} hm³`;
    }

    loadTableData() {
        for (let i = 0; i < this.data.length; i++) {
            let href = `/${this.routeLine}/dashboard/${this.data[i].name}`;
            if (this.$route.params.type != undefined) {
                href = `/${this.routeLine}/dashboard/${this.$route.params.type}/${this.data[i].name}`;
            }
            this.data[i]["route"] = href;
        }
    }
}
</script>
