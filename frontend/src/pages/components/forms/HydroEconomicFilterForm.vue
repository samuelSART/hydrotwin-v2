<template>
    <v-form v-model="formValues.valid" ref="form" lazy-validation>
        <v-subheader class="pa-0 mt-2" style="height:auto">
            {{ $t("hydroEconomicFilterForm.demandUnit") }}
        </v-subheader>
        <v-select
            dense
            :items="demandUnits"
            item-text="text"
            item-value="value"
            prepend-icon="mdi-map"
            v-model="formValues.layer"
        ></v-select>
        <v-subheader class="pa-0 mt-2" style="height:auto">
            {{ $t("hydroEconomicFilterForm.period") }}
        </v-subheader>
        <v-select
            dense
            :items="periods"
            item-text="text"
            item-value="value"
            prepend-icon="mdi-calendar"
            v-model="formValues.period"
        ></v-select>
        <v-row class="pb-2" justify="center">
            <v-btn
                color="secondary"
                class="ma-2 white--text"
                full-width
                @click="onHydroEconomicFilterUpdated"
            >
                {{ $t("WMSFilterForm.refresh") }}
                <v-icon right dark>
                    mdi-refresh
                </v-icon>
            </v-btn>
        </v-row>
    </v-form>
</template>

<script lang="ts">
import { Vue, Component, ModelSync } from "vue-property-decorator";

import { HydroEconomicFilterFormInterface, ComboBoxItem } from "@/interfaces";

@Component
export default class HydroEconomicFilterForm extends Vue {
    @ModelSync("HydroEconomicFilterForm", "change", { type: Object })
    readonly formValues!: HydroEconomicFilterFormInterface;

    demandUnits: ComboBoxItem[] = [
        {
            text: this.$t("hydroEconomicFilterForm.agriculture"),
            value: "agriculture"
        },
        { text: this.$t("hydroEconomicFilterForm.urban"), value: "urban" },
        {
            text: this.$t("hydroEconomicFilterForm.industry"),
            value: "industry"
        },
        { text: this.$t("hydroEconomicFilterForm.golf"), value: "golf" },
        { text: this.$t("hydroEconomicFilterForm.wetland"), value: "wetland" }
    ];

    periods: ComboBoxItem[] = [
        {
            text: this.$t("hydroEconomicFilterForm.monthlyMonthly"),
            value: "monthlyMonthly"
        },
        {
            text: this.$t("hydroEconomicFilterForm.monthlyDaily"),
            value: "monthlyDaily"
        },
        { text: this.$t("hydroEconomicFilterForm.daily"), value: "daily" }
    ];

    onHydroEconomicFilterUpdated() {
        this.$emit("on-hydro-economic-filter-updated");
    }
}
</script>
