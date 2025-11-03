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
                    {{ $t("aemet.search") }}
                    <v-icon right dark>mdi-refresh</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row class="d-flex justify-center ma-0">
            <v-col xs="12" sm="10" md="8">
                <v-card class="table-card">
                    <v-card-title>{{ this.loadedIdemaCode }}</v-card-title>
                    <v-simple-table>
                        <thead>
                            <tr>
                                <th>
                                    {{ this.dataType }}
                                </th>
                                <th>
                                    {{ $t("aemet.date") }}
                                </th>
                            </tr>
                        </thead>
                        <tbody v-if="this.dataType === this.dataList[0]">
                            <tr v-for="item in this.allData" :key="item.fecha">
                                <td>
                                    {{
                                        item.prec || item.prec === 0
                                            ? `${item.prec} mm`
                                            : `-`
                                    }}
                                </td>
                                <td>
                                    {{
                                        new Date(
                                            item.fecha
                                        ).toLocaleDateString()
                                    }}
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-if="this.dataType === this.dataList[1]">
                            <tr v-for="item in this.allData" :key="item.fecha">
                                <td>
                                    {{
                                        item.velmedia || item.velmedia === 0
                                            ? `${item.velmedia} m/s`
                                            : `-`
                                    }}
                                </td>
                                <td>
                                    {{
                                        new Date(
                                            item.fecha
                                        ).toLocaleDateString()
                                    }}
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-if="this.dataType === this.dataList[2]">
                            <tr v-for="item in this.allData" :key="item.fecha">
                                <td>
                                    {{
                                        item.racha || item.racha === 0
                                            ? `${item.racha} m/s`
                                            : `-`
                                    }}
                                </td>
                                <td>
                                    {{
                                        new Date(
                                            item.fecha
                                        ).toLocaleDateString()
                                    }}
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-if="this.dataType === this.dataList[3]">
                            <tr v-for="item in this.allData" :key="item.fecha">
                                <td>
                                    {{
                                        item.tmin || item.tmin === 0
                                            ? `${item.tmin} ºC`
                                            : `-`
                                    }}
                                </td>
                                <td>
                                    {{
                                        new Date(
                                            item.fecha
                                        ).toLocaleDateString()
                                    }}
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-if="this.dataType === this.dataList[4]">
                            <tr v-for="item in this.allData" :key="item.fecha">
                                <td>
                                    {{
                                        item.tmax || item.tmax === 0
                                            ? `${item.tmax} ºC`
                                            : `-`
                                    }}
                                </td>
                                <td>
                                    {{
                                        new Date(
                                            item.fecha
                                        ).toLocaleDateString()
                                    }}
                                </td>
                            </tr>
                        </tbody>
                        <tbody v-if="this.dataType === this.dataList[5]">
                            <tr v-for="item in this.allData" :key="item.fecha">
                                <td>
                                    {{
                                        item.tmed || item.tmed === 0
                                            ? `${item.tmed} ºC`
                                            : `-`
                                    }}
                                </td>
                                <td>
                                    {{
                                        new Date(
                                            item.fecha
                                        ).toLocaleDateString()
                                    }}
                                </td>
                            </tr>
                        </tbody>
                    </v-simple-table>
                </v-card>
            </v-col>
        </v-row>
    </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import { aemetConfig } from "@/config/aemet";
import { mapMutations } from "vuex";
import * as types from "@/store/types";

@Component({
    components: {
        CalendarRangeInput: () =>
            import("@/components/layout/CalendarRangeInput.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class RangeWeather extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

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

    dataList = [
        this.$t("aemet.precipitation"),
        this.$t("aemet.windAverageSpeed"),
        this.$t("aemet.maxGustOfWind"),
        this.$t("aemet.maxTemperature"),
        this.$t("aemet.minTemperature"),
        this.$t("aemet.averageTemperature")
    ];

    idemaCode = "";
    loadedIdemaCode = "";
    dates = ["", ""];
    dataUrl = "";
    show = false;
    availableDates = [];
    allData = [];
    dataType = this.dataList[0];
    maxDate;

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
        this.loadedIdemaCode = this.idemaCode;
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
                this.show = true;
                const data = await response.json();
                this.allData = data;
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
    height: 90%;
    height: calc(100vh - 152px);
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

.table-card {
    margin-top: 4px;
    height: calc(100vh - 400px);
    overflow-y: scroll;
}

i.v-icon.v-icon {
    color: #3f51b5;
}

i.v-icon.v-icon:hover {
    cursor: pointer;
}

tr:nth-of-type(even) {
    background-color: #f6f6f6;
}

tr th {
    background-color: #f6f6f6;
    border-top: thin solid rgba(0, 0, 0, 0.12);
    font-size: 0.9rem !important;
}
</style>
<style>
.date-card input:hover {
    cursor: pointer;
}
</style>
