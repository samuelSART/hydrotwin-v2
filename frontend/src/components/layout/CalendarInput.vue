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
                v-model="formatDate"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                dense
            ></v-text-field>
        </template>
        <v-date-picker
            v-model="date"
            @change="dateUpdate"
            :first-day-of-week="1"
            :events="availableDates"
            :type="type"
            locale="es-ES"
        ></v-date-picker>
    </v-menu>
</template>

<script lang="ts">
import { Vue, Component, ModelSync, Prop } from "vue-property-decorator";

import moment from "moment";

@Component
export default class CalendarInput extends Vue {
    @ModelSync("dateValue", "change", { type: String })
    readonly date?: string;
    @Prop({ type: Array, default: [], required: false })
    readonly availableDates!: Array<string>;
    @Prop({ type: String, default: "date", required: false })
    readonly type!: string;

    /**
     * Computed
     */
    get formatDate() {
        if (this.date) {
            return moment(this.date).format("DD/MM/YYYY");
        }
        return "";
    }

    dateUpdate() {
        this.$emit("on-date-updated");
    }
}
</script>

<style></style>
