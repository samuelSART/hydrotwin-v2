<template>
    <v-form class="mt-0" v-model="formValues.valid" ref="form" lazy-validation>
        <v-row>
            <v-col v-if="variablesOptions && variablesOptions.length">
                <v-subheader class="pa-0 mt-2" style="height:auto">
                    {{ $t("damVariablesDialog.variable") }}
                </v-subheader>
                <v-select
                    dense
                    :items="variablesOptions"
                    item-text="text"
                    item-value="value"
                    v-model="formValues.variable"
                    :rules="formRules.variable"
                ></v-select>
            </v-col>
            <v-col v-if="timeRangesOptions && timeRangesOptions.length">
                <v-subheader class="pa-0 mt-2" style="height:auto">
                    {{ $t("damVariablesDialog.timeRange") }}
                </v-subheader>
                <v-select
                    dense
                    :items="timeRangesOptions"
                    item-text="text"
                    item-value="value"
                    v-model="formValues.timeRange"
                    @change="checkCustomTimeRange"
                    :rules="formRules.timeRange"
                ></v-select>
            </v-col>
            <v-col>
                <v-subheader class="pa-0 mt-2" style="height:auto">
                    {{ $t("damVariablesDialog.customTimeRange") }}
                </v-subheader>
                <CalendarRangeInput
                    v-model="formValues.customTimeRange"
                    :disabled="customTimeRangeDisabled"
                    :rules="formRules.customTimeRange"
                />
            </v-col>
        </v-row>

        <v-row v-if="predictionsShown || simulationsShown">
            <v-divider class="mx-2"></v-divider>
        </v-row>

        <!-- predictions & simulations section -->
        <v-row>
            <v-col>
                <v-card tile elevation="0">
                    <v-card-text class="pa-0 pl-2">
                        <v-row>
                            <!-- prediction options -->
                            <v-col v-if="predictionsShown">
                                <SelectActivator
                                    v-model="predictions"
                                    :enabled="formValues.predictionEnabled"
                                    :options="predictionsOptions"
                                    :defaultOption="formValues.forecasting"
                                    :labelText="predictionsTexts.label"
                                    :subheaderText="predictionsTexts.subheader"
                                    @on-selected="handlePredictionOnSelect"
                                />
                            </v-col>

                            <!-- simulation options -->
                            <v-col v-if="simulationsShown">
                                <SelectActivator
                                    v-model="simulations"
                                    :enabled="formValues.simulationEnabled"
                                    :options="simulationsOptions"
                                    :defaultOption="formValues.simulation"
                                    :labelText="simulationsTexts.label"
                                    :subheaderText="simulationsTexts.subheader"
                                    @on-selected="handleSimulationOnSelect"
                                />
                            </v-col>
                        </v-row>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <v-row>
            <v-col align-self="center">
                <v-btn
                    color="secondary"
                    class="white--text"
                    @click="handleRefresh"
                >
                    {{ $t("damVariablesDialog.refresh") }}
                    <v-icon right dark>mdi-refresh</v-icon>
                </v-btn>
            </v-col>
        </v-row>
    </v-form>
</template>

<script lang="ts">
import { Component, Ref, Vue, Prop, ModelSync } from "vue-property-decorator";

import {
    ComboBoxItem,
    BasicFormInterface,
    FormBtnAction,
    FormActions
} from "@/interfaces";

@Component({
    components: {
        CalendarRangeInput: () =>
            import("@/components/layout/CalendarRangeInput.vue"),
        SelectActivator: () => import("@/components/forms/SelectActivator.vue")
    }
})
export default class BasicForm extends Vue {
    @ModelSync("form", "change", {
        type: Object,
        default: {
            valid: false,
            variable: "",
            timeRange: "",
            customTimeRange: []
        }
    })
    formValues!: BasicFormInterface;

    @Ref("form") readonly formActions!: FormActions;

    @Prop({ type: Array, required: false, default: null })
    variablesOptions!: ComboBoxItem[] | null;

    @Prop({ type: Array, required: false, default: null })
    timeRangesOptions!: ComboBoxItem[] | null;

    @Prop({ type: Array, required: false, default: null })
    predictionsOptions!: ComboBoxItem[] | null;

    @Prop({ type: Array, required: false, default: null })
    simulationsOptions!: ComboBoxItem[] | null;

    customTimeRangeDisabled = true;
    formRules = {
        variable: [v => !!v || this.$t("damVariablesDialog.variableRequired")],
        timeRange: [
            v => !!v || this.$t("damVariablesDialog.timeRangeRequired")
        ],
        customTimeRange: [v => this.customTimeRangeRule(v)]
    };

    predictions = false;
    simulations = false;

    predictionsTexts = {
        label: this.$t("form.predictions.predictions"),
        subheader: this.$t("form.predictions.forecastType")
    };

    simulationsTexts = {
        label: this.$t("form.simulations.simulations"),
        subheader: this.$t("form.simulations.simulationType")
    };

    customTimeRangeRule(v) {
        if (this.formValues.timeRange === "custom" && v === "") {
            return String(
                this.$t("damVariablesDialog.customTimeRangeRequired")
            );
        } else {
            return true;
        }
    }

    /**
     * Check if the custom time range is selected
     */
    checkCustomTimeRange(): void {
        if (this.formValues.timeRange === "custom") {
            this.customTimeRangeDisabled = false;
        } else {
            this.customTimeRangeDisabled = true;
        }
    }

    handlePredictionOnSelect(value: number): void {
        this.formValues.forecasting = value;
    }

    handleSimulationOnSelect(value: number): void {
        this.formValues.simulation = value;
    }

    /**
     * Handle the form submit
     */
    handleRefresh(): void {
        if (!this.formActions.validate()) return;

        const { startDate, endDate } = this.getDateLimits();

        let params: FormBtnAction = {
            variable: this.formValues.variable,
            startDate,
            endDate
        };

        /**
         * Forecasting & Simulation params
         */
        params = {
            ...params,
            forecasting: this.predictions
                ? this.formValues.forecasting
                : undefined,
            simulation: this.simulations
                ? this.formValues.simulation
                : undefined
        };

        /**
         * Emit event
         */
        this.$emit("on-refresh", params);
    }

    /**
     * Reset validations
     */
    resetValidation(): void {
        this.formActions.resetValidation();
    }

    /**
     * Get start and end dates
     */
    getDateLimits() {
        let startDate: Date, endDate: Date;

        if (this.formValues.timeRange === "custom") {
            this.formValues.customTimeRange.sort((a, b) => {
                return new Date(a).getTime() - new Date(b).getTime();
            });
            startDate = new Date(this.formValues.customTimeRange[0]);
            endDate = new Date(
                new Date(this.formValues.customTimeRange[1]).setHours(
                    23,
                    59,
                    59
                )
            );
        } else {
            startDate = new Date(
                new Date().setDate(
                    new Date().getDate() - parseInt(this.formValues.timeRange)
                )
            );

            endDate = new Date(new Date().setHours(23, 59, 59));
        }

        return { startDate, endDate };
    }

    get predictionsShown() {
        return this.predictionsOptions && this.predictionsOptions.length;
    }

    get simulationsShown() {
        return this.simulationsOptions && this.simulationsOptions.length;
    }
}
</script>

<style scoped></style>
