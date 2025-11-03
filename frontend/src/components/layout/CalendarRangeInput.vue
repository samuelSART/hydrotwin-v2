<template>
    <v-menu
        :close-on-content-click="false"
        :nudge-right="40"
        transition="scale-transition"
        offset-y
        min-width="290px"
    >
        <template v-slot:activator="{ on, attrs }">
            <v-text-field
                v-model="dateRangeText"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                dense
                :disabled="disabled"
                :rules="rules"
            ></v-text-field>
        </template>
        <v-date-picker
            v-model="dates"
            range
            :disabled="disabled"
            :locale="$i18n.locale"
        ></v-date-picker>
    </v-menu>
</template>

<script lang="ts">
import { Vue, Component, Prop, ModelSync } from "vue-property-decorator";

@Component
export default class CalendarRangeInput extends Vue {
    @ModelSync("datesValue", "change", { type: Array })
    readonly dates?: string[];

    @Prop({ type: Boolean, default: true, required: false })
    readonly disabled!: boolean;

    @Prop({ type: Array, required: false })
    rules!: string[];

    /**
     * Computed
     */
    get dateRangeText() {
        if (this.dates) {
            if (
                new Date(this.dates[0]).getTime() >
                new Date(this.dates[1]).getTime()
            ) {
                return `${this.dates[1]}  ~  ${this.dates[0]}`;
            } else if (
                new Date(this.dates[0]).getTime() <
                new Date(this.dates[1]).getTime()
            ) {
                return `${this.dates[0]}  ~  ${this.dates[1]}`;
            }
        }
        return "";
    }
}
</script>

<style></style>
