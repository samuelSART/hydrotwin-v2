<template>
    <div class="wrap my-5">
        <v-row class="d-flex justify-center ma-0">
            <v-col class="my-0 py-0" xs="6" sm="5" md="4">
                <v-autocomplete
                    dense
                    v-model="idemaCode"
                    :items="especificDayIdema"
                    :label="$t('aemet.weatherStation')"
                ></v-autocomplete>
            </v-col>
            <v-col class="my-0 py-0" xs="6" sm="5" md="4">
                <v-autocomplete
                    dense
                    v-model="dataType"
                    :items="dataList"
                    :label="$t('aemet.datatype')"
                    @change="dataKeyMap()"
                >
                </v-autocomplete>
            </v-col>
        </v-row>
        <v-row class="d-flex justify-center ma-0">
            <v-col class="my-0 py-0" xs="6" sm="5" md="4">
                <CalendarRangeInput
                    v-model="dates"
                    :disabled="false"
                ></CalendarRangeInput>
            </v-col>
            <v-col class="my-0 py-0" xs="6" sm="5" md="4">
                <v-btn
                    color="secondary"
                    class="white--text"
                    @click="fetchUrl"
                    block
                >
                    {{ $t("aemet.generateChart") }}
                    <v-icon right dark>mdi-refresh</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row class="d-flex justify-center ma-0">
            <OptionChart
                ref="chart"
                height="calc(100vh - 400px)"
                width="calc(100vw - 350px)"
                :chart-options="aemetChartOption"
            />
        </v-row>
    </div>
</template>

<script lang="ts">
import { Vue, Component, Ref } from "vue-property-decorator";
import { EChartsOption } from "echarts";
import { aemetConfig } from "@/config/aemet";
import OptionChart from "../charts/OptionChart.vue";
import { VariableValue } from "@/interfaces";
import { getLineChartOption, getEmptyOption } from "@/config/charts";
import { mapMutations } from "vuex";
import * as types from "@/store/types";

const AEMET_VARIABLES = new Map<string, string>([
    ["prec", "Precipitación (mm)"],
    ["velmedia", "Velocidad media del viento (m/s)"],
    ["racha", "Racha máxima del viento (m/s)"],
    ["tmin", "Temperatura mínima (ºC)"],
    ["tmax", "Temperatura máxima (ºC)"],
    ["tmed", "Temperatura media (ºC)"]
]);

@Component({
    components: {
        CalendarRangeInput: () =>
            import("@/components/layout/CalendarRangeInput.vue"),
        OptionChart: () => import("@/components/charts/OptionChart.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class WeatherChart extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @Ref("chart") readonly chart!: OptionChart;

    aemetChartOption: EChartsOption = {};
    loading = false;

    especificDayIdema = [
        "7002Y - ÁGUILAS",
        "7012C - CARTAGENA",
        "7031 - SAN JAVIER AEROPUERTO",
        "7031X - SAN JAVIER AEROPUERTO",
        "7096B - HELLÍN",
        "7119B - CARAVACA DE LA CRUZ",
        "7145D - CIEZA",
        "7178I - MURCIA",
        "7209 - LORCA",
        "7228 - ALCANTARILLA, BASE AÉREA",
        "7247X - EL PINÓS/PINOSO",
        "7275C - YECLA"
    ];

    dataList = Array.from(AEMET_VARIABLES.values());

    idemaCode = "";
    dates = ["", ""];
    dataUrl = "";
    allData = [];
    selectedData = [];
    dataType = "";
    dataKey = "";

    //convert AEMET_VARIABLES key into value
    dataKeyMap() {
        for (const [key, value] of AEMET_VARIABLES) {
            if (value === this.dataType) {
                this.dataKey = key;
            }
        }
    }

    initialDate() {
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() - 4);
        const minDate = new Date();
        minDate.setDate(minDate.getDate() - 8);

        this.dates = [
            minDate.toISOString().split("T")[0],
            maxDate.toISOString().split("T")[0]
        ];
    }

    mounted() {
        this.initialDate();
    }

    orderDates() {
        if (this.dates) {
            if (
                new Date(this.dates[0]).getTime() >
                new Date(this.dates[1]).getTime()
            ) {
                this.dates = [this.dates[1], this.dates[0]];
            } else if (
                new Date(this.dates[0]).getTime() <
                new Date(this.dates[1]).getTime()
            ) {
                this.dates = [this.dates[0], this.dates[1]];
            } else if (
                new Date(this.dates[0]).getTime() ===
                    new Date(this.dates[1]).getTime() ||
                !this.dates[1]
            ) {
                this.dates = [this.dates[0], this.dates[0]];
            }
        }
        return "";
    }

    async fetchUrl() {
        this.orderDates();
        try {
            const response = await fetch(
                `https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/${
                    this.dates[0]
                }T00%3A00%3A00UTC/fechafin/${
                    this.dates[1]
                }T23%3A59%3A59UTC/estacion/${
                    this.idemaCode.split(" ")[0]
                }?api_key=${aemetConfig.accessToken}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "cache-control": "no-cache"
                    }
                }
            );
            if (response.ok) {
                const data = await response.json();
                this.dataUrl = data.datos;
                this.fetchData();
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(this.$t("aemet.noData").toString());
            }
        }
    }

    async fetchData() {
        try {
            this.setProgressBar(true);
            const response = await fetch(`${this.dataUrl}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json; charset=utf-8",
                    "cache-control": "no-cache"
                }
            });
            if (response.ok) {
                const data = await response.json();
                this.allData = data;
                this.selectedData = data.map(item => [
                    new Date(item["fecha"]).getTime(),
                    Number(item[this.dataKey].replace(",", "."))
                ]);
                this.updateAemetVariablePlot(this.selectedData);
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(this.$t("aemet.noData").toString());
            }
        } finally {
            this.setProgressBar(false);
        }
    }

    /**
     * Plot aemet variable
     */
    updateAemetVariablePlot(values: VariableValue[]): void {
        if (!values || !values.length) {
            this.aemetChartOption = {
                ...getEmptyOption(`${this.$t("chart.noData")}`)
            };
            return;
        } else if (values.length < 5) {
            this.aemetChartOption = {
                ...getEmptyOption(`${this.$t("aemet.setRange")}`)
            };
            return;
        }

        this.aemetChartOption = getLineChartOption({});

        /**
         * XAxis
         */
        this.aemetChartOption.xAxis = {
            ...this.aemetChartOption.xAxis,
            data: undefined,
            type: "time",
            splitArea: {
                show: false
            }
        };

        this.aemetChartOption.title = {
            left: "center",
            text: `${this.dataType}`
        };

        this.aemetChartOption.toolbox = {
            feature: {
                dataZoom: {
                    yAxisIndex: "none"
                },
                restore: {}
            }
        };

        const serieCopy = this.aemetChartOption.series
            ? { ...this.aemetChartOption.series[0] }
            : {};

        this.aemetChartOption.series = [];
        this.aemetChartOption.series.push({
            ...serieCopy,
            name: this.$t("measPointDialog.value"),
            data: values,
            symbol: "none"
        });
    }

    /**
     * Show error message
     * @param {string} error Error message
     * @return {void}
     */
    showError(error: string): void {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>

<style lang="scss" scoped>
.wrap {
    width: 100%;
}

.date-card {
    border-bottom: 1px solid #888888;
    margin-top: 4px;

    input {
        width: 100%;
        color: #555555;
    }
}

i.v-icon.v-icon {
    color: #3f51b5;
}

i.v-icon.v-icon:hover {
    cursor: pointer;
}
</style>
<style>
.date-card input:hover {
    cursor: pointer;
}
</style>
