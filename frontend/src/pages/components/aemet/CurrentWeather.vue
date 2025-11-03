<template>
    <div class="my-5">
        <v-row class="d-flex justify-center ma-0">
            <v-col class="my-0 py-0" xs="12" sm="10" md="8">
                <v-autocomplete
                    v-model="idemaCode"
                    :items="currentIdema"
                    dense
                    :label="$t('aemet.weatherStation')"
                ></v-autocomplete>
            </v-col>
        </v-row>
        <v-row class="d-flex justify-center ma-0">
            <v-col xs="12" sm="10" md="8">
                <v-card>
                    <v-simple-table>
                        <thead>
                            <tr>
                                <th colSpan="2">
                                    {{ this.apiData.ubi ? this.idemaCode : `` }}
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{
                                        $t("aemet.lastActualization")
                                    }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.lastActualizationInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.fint
                                            ? `${
                                                  this.apiData.fint.split(
                                                      "T"
                                                  )[1]
                                              }`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{ $t("aemet.altitude") }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.altitudeInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.alt ||
                                        this.apiData.alt === 0
                                            ? `${this.apiData.alt} m`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{
                                        $t("aemet.lastHourRainfall")
                                    }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.lastHourRainfallInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.prec ||
                                        this.apiData.prec === 0
                                            ? `${this.apiData.prec} mm`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{ $t("aemet.windSpeed") }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.windSpeedInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.vv || this.apiData.vv === 0
                                            ? `${this.apiData.vv} m/s`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{ $t("aemet.windDirection") }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.windDirectionInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.dv || this.apiData.dv === 0
                                            ? `${this.apiData.dv}º`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{
                                        $t("aemet.soilTemperature")
                                    }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.soilTemperatureInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.ts || this.apiData.ts === 0
                                            ? `${this.apiData.ts}ºC`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{
                                        $t("aemet.airTemperature")
                                    }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.airTemperratureInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.ta || this.apiData.ta === 0
                                            ? `${this.apiData.ta}ºC`
                                            : `-`
                                    }}
                                </td>
                            </tr>
                            <tr>
                                <th
                                    class="d-flex align-center justify-space-between"
                                >
                                    <span>{{
                                        $t("aemet.relativeHumidity")
                                    }}</span>
                                    <v-tooltip top v-if="this.apiData.fint">
                                        <template
                                            v-slot:activator="{ on, attrs }"
                                            ><v-icon v-bind="attrs" v-on="on"
                                                >mdi-information-outline</v-icon
                                            >
                                        </template>
                                        <span>{{
                                            $t("aemet.relativeHumidityInfo")
                                        }}</span>
                                    </v-tooltip>
                                </th>
                                <td>
                                    {{
                                        this.apiData.hr || this.apiData.hr === 0
                                            ? `${this.apiData.hr}%`
                                            : `-`
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
import { Vue, Component, Watch } from "vue-property-decorator";
import { aemetConfig } from "@/config/aemet";
import { mapMutations } from "vuex";
import * as types from "@/store/types";

@Component({
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class CurrentWeather extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    currentIdema = [
        "7002Y - ÁGUILAS",
        "7012C - CARTAGENA",
        "7023X - FUENTE ALAMO",
        "7026X - TORRE PACHECO (C.C.A. AUT.)",
        "7031X - MURCIA/SAN JAVIER",
        "7066Y - EMBALSE DE LA FUENSANTA (AUTOMÁTICA)",
        "7072Y - SEGE",
        "7080X - BENIZAR",
        "7096B - HELLÍN",
        "7103Y - TOBARRA",
        "7119B - CARAVACA FUENTES DEL MARQUÉS",
        "7121A - CALASPARRA",
        "7127X - BULLAS",
        "7138B - JUMILLA EL ALBAL",
        "7145D - CIEZA PARQUE DE BOMBEROS",
        "7158X - ARCHENA",
        "7172X - MULA (P. BOMBEROS - AUT.)",
        "7178I - MURCIA",
        "7195X - CARAVACA (LOS ROYOS - AUT.)",
        "7203A - ZARZILLA DE RAMOS",
        "7209 - LORCA",
        "7211B - PUERTO LUMBRERAS",
        "7227X - ALHAMA (COMARZA - AUT.)",
        "7237E - MOLINA DE SEGURA (LOS VALIENTES)",
        "7244X - ORIHUELA DESAMPARADOS",
        "7247X - PINOSO",
        "7250C - ABANILLA",
        "7261X - ROJALES EL MOLINO",
        "7275C - YECLA"
    ];

    idemaCode = "";
    dataUrl = "";
    apiData = [];
    show = false;

    @Watch("idemaCode")
    async fetchUrl() {
        try {
            this.setProgressBar(true);
            const response = await fetch(
                `https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/${
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
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(this.$t("aemet.error").toString());
            }
        } finally {
            this.setProgressBar(false);
        }
    }

    @Watch("dataUrl")
    async fetchData() {
        try {
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
                this.apiData = data[data.length - 1];
            }
        } catch (error) {
            if (error instanceof Error) {
                this.showError(this.$t("aemet.error").toString());
            }
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
i.v-icon.v-icon {
    color: #3f51b5;
}

i.v-icon.v-icon:hover {
    cursor: pointer;
}
</style>
<style></style>
