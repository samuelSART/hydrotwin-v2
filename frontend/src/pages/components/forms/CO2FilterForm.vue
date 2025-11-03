<template>
    <v-form v-model="formValues.valid" ref="form" lazy-validation>
        <v-subheader class="pa-0 mt-2" style="height:auto">
            {{ $t("CO2FilterForm.demandUnit") }}
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
            {{ $t("CO2FilterForm.period") }}
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
                @click="onCO2FilterUpdated"
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
import { CO2FilterFormInterface, ComboBoxItem } from "@/interfaces";

@Component
export default class CO2FilterForm extends Vue {
    @ModelSync("CO2FilterForm", "change", { type: Object })
    readonly formValues!: CO2FilterFormInterface;

    demandUnits: ComboBoxItem[] = [
        { text: this.$t("CO2FilterForm.agriculture"), value: "agriculture" },
        { text: this.$t("CO2FilterForm.urban"), value: "urban" },
        { text: this.$t("CO2FilterForm.industry"), value: "industry" },
        { text: this.$t("CO2FilterForm.golf"), value: "golf" },
        { text: this.$t("CO2FilterForm.wetland"), value: "wetland" }
    ];

    periods: ComboBoxItem[] = [
        {
            text: this.$t("CO2FilterForm.monthlyMonthly"),
            value: "monthlyMonthly"
        },
        {
            text: this.$t("CO2FilterForm.monthlyDaily"),
            value: "monthlyDaily"
        },
        { text: this.$t("CO2FilterForm.daily"), value: "daily" }
    ];

    onCO2FilterUpdated() {
        this.$emit("on-co2-filter-updated", {
            layer: this.formValues.layer,
            period: this.formValues.period
        });
    }
}
</script>
