<template>
    <v-form v-model="formValues.valid" ref="form" lazy-validation>
        <v-subheader class="pa-0 mt-2" style="height:auto">
            {{ $t("CPPiezometerFilterForm.timeRange") }}
        </v-subheader>
        <v-select
            dense
            :items="ranges"
            item-text="text"
            item-value="value"
            prepend-icon="mdi-clock"
            v-model="formValues.timeRange"
            required
        ></v-select>

        <v-subheader class="pa-0 mt-0" style="height:auto">
            {{ $t("CPPiezometerFilterForm.piezometersShown") }}
        </v-subheader>
        <v-switch v-model="formValues.layerPzmtrs" class="ma-0"></v-switch>

        <v-subheader class="pa-0 mt-0" style="height:auto">
            {{ $t("CPPiezometerFilterForm.aquifersShown") }}
        </v-subheader>
        <v-switch v-model="formValues.layerAqfrs" class="ma-0"></v-switch>

        <v-row class="pb-2" justify="center">
            <v-btn
                color="secondary"
                class="ma-2 white--text"
                @click="onFilterUpdated"
                full-width
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
import { Component, Vue, ModelSync } from "vue-property-decorator";
import { CPPiezometerForm, ComboBoxItem } from "@/interfaces";
import { cpTimeRangesPieConfig } from "@/pages/piezometry/cppiezometersconfig";

@Component
export default class CPPiezometerFilterForm extends Vue {
    @ModelSync("form", "change", {
        type: Object,
        default: {
            valid: true,
            timeRange: "",
            layerPzmtrs: true,
            layerAqfrs: true
        }
    })
    formValues!: CPPiezometerForm;

    ranges: ComboBoxItem[] = cpTimeRangesPieConfig.map(trc => {
        return {
            text: this.$t(`CPPiezometerFilterForm.${trc.range}`),
            value: trc.range
        };
    });

    onFilterUpdated() {
        this.$emit("on-filter-updated");
    }
}
</script>

<style scoped></style>
