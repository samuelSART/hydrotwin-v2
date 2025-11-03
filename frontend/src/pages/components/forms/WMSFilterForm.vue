<template>
    <v-form v-model="formValues.valid" ref="form">
        <v-subheader class="pa-0 mt-2" style="height:auto">
            {{ $t("WMSFilterForm.layer") }}
        </v-subheader>
        <v-select
            dense
            :items="layers"
            item-text="text"
            item-value="value"
            prepend-icon="mdi-map"
            v-model="formValues.layer"
            :rules="formRules.layer"
            @change="
                fetchStyles();
                fetchDates();
                disableNavigation();
            "
            required
        ></v-select>

        <v-subheader class="pa-0 mt-2" style="height:auto">
            {{ $t("WMSFilterForm.style") }}
        </v-subheader>
        <v-select
            dense
            :items="styles"
            item-text="text"
            item-value="value"
            prepend-icon="mdi-palette-swatch-variant"
            v-model="formValues.style"
            @change="onFilterUpdated"
            :rules="formRules.style"
            required
        ></v-select>
        <v-subheader class="pa-0 mt-2" style="height:auto">
            Selected date
        </v-subheader>
        <v-row>
            <v-col class=" mb-2 pb-0">
                <CalendarInput
                    v-model="formValues.selectedDate"
                    @on-date-updated="adjustAvailableDates"
                    @change="onFilterUpdated"
                    :availableDates="availableDates"
                />
            </v-col>
        </v-row>
        <v-row class="mt-0 mb-0 pt-0 pb-0">
            <v-col class="mt-0 mb-0 pt-0 pb-0">
                <v-btn
                    icon
                    block
                    color="blue"
                    :disabled="navDisabled"
                    @click="onPreviousDay"
                >
                    <v-icon>mdi-arrow-left</v-icon>
                </v-btn>
            </v-col>

            <v-col class="mt-0 mb-0 pt-0 pb-0">
                <v-btn
                    icon
                    block
                    color="blue"
                    :disabled="navDisabled"
                    @click="onNextDay"
                >
                    <v-icon>mdi-arrow-right</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row class="mt-0 mb-0 pt-0 pb-0">
            <v-col class="mt-0 mb-0 pt-0 pb-0">
                <v-btn
                    icon
                    block
                    small
                    prepend-icon="mdi-download"
                    :disabled="navDisabled"
                    @click="downloadCSV"
                >  <v-icon>mdi-download</v-icon> {{ $t("WMSFilterForm.Download_UDA_stats") }} 
                </v-btn>
            </v-col>

            <v-col class="mt-0 mb-0 pt-0 pb-0">
                <v-btn
                    icon
                    block
                    small
                    prepend-icon="mdi-download"
                    :disabled="navDisabled"
                    @click="downloadRaster"
                >  <v-icon>mdi-download</v-icon> {{ $t("WMSFilterForm.Download_raster") }} 
                </v-btn>
            </v-col>
        </v-row>
    </v-form>
</template>

<script lang="ts">
import {
    Vue,
    Component,
    ModelSync,
    Prop,
    Ref,
    Watch
} from "vue-property-decorator";
import { mapMutations } from "vuex";

import {
    WMSFilterFormInterface,
    FormActions,
    ComboBoxItem,
    ResponseDataLayer as rdl,
    RespondeDataStyles as rds,
    ResponseLayerDates,
    ResponseDownloadData
} from "@/interfaces";
import * as types from "@/store/types";
import { downloadCSV } from "@/utils";

@Component({
    components: {
        FilterFormPanelBase: () =>
            import("@/components/layout/FilterFormPanelBase.vue"),
        CalendarInput: () => import("@/components/layout/CalendarInput.vue")
    },
    methods: {
        ...mapMutations({
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class WMSFilterForm extends Vue {
    @ModelSync("WMSFilterForm", "change", { type: Object })
    readonly formValues!: WMSFilterFormInterface;

    @Prop({ type: Boolean, default: true, required: false })
    readonly displayDates!: boolean;

    @Ref("form") readonly formActions!: FormActions;

    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    layers: ComboBoxItem[] = [];
    styles: ComboBoxItem[] = [];
    availableDates: Array<string> = [];
    currentDayIndex = -1;
    navDisabled = true;
    formRules = {
        layer: [v => !!v || "Layer is required"],
        style: [v => !!v || "Style is required"]
    };

    @Watch("formValues.line")
    async onLineUpdate() {
        this.fetchData();
    }

    mounted() {
        this.fetchData();
    }

    /**
     * Methods
     */
    fetchData() {
        this.fetchLayers();
    }

    async fetchLayers() {
        try {
            this.clearData();
            this.clearForm();
            const layersResponse = await this.$api.getLayers<rdl>(
                this.formValues.line
            );
            if (layersResponse.ok) {
                this.layers = layersResponse.data.map(layer => {
                    return {
                        text: this.$t(`WMSFilterForm.${layer.layer}`),
                        value: layer
                    };
                });
                this.formValues.layer = layersResponse.data[0];
                await this.fetchStyles();
                await this.fetchDates();
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(`${this.$t("netError")}`);
                this.formValues.valid = false;
            }
        }
    }

    async fetchStyles() {
        try {
            this.formValues.valid = false;
            this.formValues.style = {
                style: "",
                title: ""
            };
            this.styles = [];
            const stylesResponse = await this.$api.getStyles<rds>(
                this.formValues.layer.layer
            );

            if (stylesResponse.ok) {
                this.styles = stylesResponse.data.styles.map(style => {
                    return {
                        text: this.$t(`WMSFilterForm.${style.style}`),
                        value: style
                    };
                });
                this.formValues.style = stylesResponse.data.styles[0];
                this.onFilterUpdated();
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(`${this.$t("netError")}`);
                this.formValues.valid = false;
            }
        }
    }

    async fetchDates() {
        try {
            this.formValues.selectedDate = new Date()
                .toISOString()
                .split("T")[0];
            this.formValues.valid = false;
            this.availableDates = [];
            this.currentDayIndex = -1;
            const datesResponse = await this.$api.getDates<ResponseLayerDates>(
                this.formValues.layer.layer
            );
            if (datesResponse.ok) {
                this.availableDates = datesResponse.data;
                this.adjustAvailableDates();
                this.onFilterUpdated();
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(`${this.$t("netError")}`);
                this.formValues.valid = false;
            }
        }
    }

    adjustAvailableDates() {
        const currentDate = new Date(this.formValues.selectedDate);
        if (this.availableDates.length != 0) {
            let minDifference = Math.abs(
                currentDate.getTime() -
                    new Date(this.availableDates[0]).getTime()
            );
            this.currentDayIndex = 0;
            for (let step = 1; step < this.availableDates.length; step++) {
                const diff = Math.abs(
                    currentDate.getTime() -
                        new Date(this.availableDates[step]).getTime()
                );
                if (diff < minDifference) {
                    minDifference = diff;
                    this.currentDayIndex = step;
                } else {
                    step = this.availableDates.length;
                }
            }
            this.formValues.selectedDate = new Date(
                new Date(this.availableDates[this.currentDayIndex])
            )
                .toISOString()
                .split("T")[0];
            
        }
    }

    disableNavigation() {
        this.formValues.valid = false;
        this.navDisabled = true;
    }

    clearForm() {
        this.formValues.valid = false;
        this.formValues.layer = {
            layer: "",
            title: ""
        };
        this.formValues.style = {
            style: "",
            title: ""
        };
        this.formValues.selectedDate = new Date().toISOString().split("T")[0];
    }

    clearData() {
        this.layers = [];
        this.styles = [];
        this.availableDates = [];
        this.currentDayIndex = -1;
        this.disableNavigation();
    }

    onFilterUpdated() {
        if (this.formActions.validate()) {
            if (
                this.currentDayIndex != -1 &&
                this.formValues.style.style != ""
            ) {
                this.navDisabled = false;
                this.formValues.valid = true;
                this.$emit("on-wms-filter-updated");
            }
        }
    }

    onPreviousDay() {
        if (0 < this.currentDayIndex) {
            this.currentDayIndex -= 1;
            this.formValues.selectedDate = new Date(
                new Date(this.availableDates[this.currentDayIndex])
            )
                .toISOString()
                .split("T")[0];
            this.onFilterUpdated();
        }
    }

    onNextDay() {
        if (this.currentDayIndex < this.availableDates.length - 1) {
            this.currentDayIndex += 1;
            this.formValues.selectedDate = new Date(
                new Date(this.availableDates[this.currentDayIndex])
            )
                .toISOString()
                .split("T")[0];
            this.onFilterUpdated();
        }
    }

    async downloadCSV() {
        
        const response = await this.$api.downloadDemandUnitRasterStats<ResponseDownloadData>(
            this.formValues.selectedDate,
            this.formValues.layer.layer  
        );
        if (!response) return;
        if (response.status == 204){
            this.showError(String(this.$t("NoDataToDownload")));
            return;
        }
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `UDA_stats_${this.formValues.layer.layer }_${this.formValues.selectedDate}.csv`);
        document.body.appendChild(link)
        link.click();
    }

    async downloadRaster() {
        const response = await this.$api.downloadRaster<ResponseDownloadData>(
            this.formValues.selectedDate,
            this.formValues.layer.layer  
        );
        if (!response) return;
        if (response.status == 204){
            this.showError(String(this.$t("NoDataToDownload")));
            return;
        }
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${this.formValues.layer.layer }_${this.formValues.selectedDate}.tif`);
        document.body.appendChild(link)
        link.click();
    }

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>

<style lang="scss" scoped></style>
