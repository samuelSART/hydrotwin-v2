<template>
    <div class="wrap">
        <v-row class="d-flex justify-center mt-3 mb-1">
            <v-col class="my-0 py-0" xs="4" sm="4" md="3">
                <v-autocomplete
                    dense
                    v-model="state"
                    :items="states"
                    :label="$t('droughtIndices.state')"
                ></v-autocomplete>
            </v-col>
            <v-col class="my-0 py-0" xs="4" sm="4" md="3">
                <CalendarInput
                    v-model="month"
                    @change="formatMonth"
                    type="month"
                    :availableDates="[]"
                />
            </v-col>
            <v-col class="my-0 py-0" xs="4" sm="4" md="3">
                <v-btn
                    color="secondary"
                    class="white--text"
                    @click="fetchDroughtIndices()"
                    block
                >
                    {{ $t("droughtIndices.fetchData") }}
                    <v-icon right dark>mdi-refresh</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <MapBox :center="mapCenter" :zoom="mapZoom" @loaded="onMapLoaded">
            <template v-slot:legend>
                <div class="pa-2">
                    <v-container>
                        <v-row
                            align="center"
                            justify="center"
                            v-for="({ color, text }, index) in legendItems"
                            :key="index"
                        >
                            <v-col class="pa-0">
                                <div class="d-flex flex-row">
                                    <span
                                        style="height: 15px; width: 30px;"
                                        :style="{
                                            'background-color': color
                                        }"
                                        class="mr-2 align-self-center"
                                    ></span>
                                    <div class="text-caption align-self-center">
                                        {{ text }}
                                    </div>
                                </div>
                            </v-col>
                        </v-row>
                    </v-container>
                </div>
            </template>
        </MapBox>
    </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapMutations } from "vuex";
import { Map as MBMap, LngLat, AnySourceImpl, GeoJSONSource } from "mapbox-gl";
import { FeatureCollection } from "geojson";

import * as types from "@/store/types";
import { SystemUnitsResponse, DroughtIndicesResponse } from "@/interfaces";

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        CalendarInput: () => import("@/components/layout/CalendarInput.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class DroughtMaps extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.636256, 37.98);
    mapZoom = 8;
    mapFeatures;

    mapData;
    month = "2022-10";
    formattedMonth = "";
    states = [
        this.$t("droughtIndices.conjuncturalShortage"),
        this.$t("droughtIndices.prolongedDrought")
    ];
    state = this.states[0];

    colorI = "white";
    colorII = "white";
    colorIII = "white";
    colorIV = "white";

    legendItems = [
        { color: "", text: "" },
        { color: "", text: "" },
        { color: "", text: "" },
        { color: "", text: "" }
    ];

    actualMonth() {
        const date = new Date();
        const year = date.getFullYear();
        const month = date.getMonth();
        this.month = `${year}-${month < 10 ? "0" + month : month}`;
    }

    formatMonth() {
        this.formattedMonth = this.month + "-01";
    }

    mounted() {
        this.actualMonth();
        this.formatMonth();
    }

    async fetchDroughtIndices() {
        try {
            this.setProgressBar(true);
            const allData = {
                type: "day",
                date: [this.formattedMonth]
            };

            const droughtIndices = await this.$api.getDroughtIndices<
                DroughtIndicesResponse
            >(allData);

            if (droughtIndices.ok) {
                this.mapData = droughtIndices.data[0];
                if (this.state === this.states[0]) {
                    this.getShortageColors();
                }
                if (this.state === this.states[1]) {
                    this.getDroughtColors();
                }
            }
        } catch (error) {
            this.setInfoMessage({
                shown: true,
                text: this.$t("droughtIndices.noData").toString()
            });
        } finally {
            this.setProgressBar(false);
        }
    }

    getShortageColors() {
        if (this.mapData.GLOBAL >= 0.5) {
            this.colorI = "yellowGreen";
        } else if (this.mapData.GLOBAL < 0.5 && this.mapData.GLOBAL >= 0.3) {
            this.colorI = "yellow";
        } else if (this.mapData.GLOBAL < 0.3 && this.mapData.GLOBAL >= 0.15) {
            this.colorI = "orange";
        } else if (this.mapData.GLOBAL != null && this.mapData.GLOBAL < 0.15) {
            this.colorI = "red";
        } else {
            this.colorI = "gray";
        }
        if (this.mapData.UTE_II_Cabecera >= 0.5) {
            this.colorII = "yellowGreen";
        } else if (
            this.mapData.UTE_II_Cabecera < 0.5 &&
            this.mapData.UTE_II_Cabecera >= 0.3
        ) {
            this.colorII = "yellow";
        } else if (
            this.mapData.UTE_II_Cabecera < 0.3 &&
            this.mapData.UTE_II_Cabecera >= 0.15
        ) {
            this.colorII = "orange";
        } else if (
            this.mapData.UTE_II_Cabecera != null &&
            this.mapData.UTE_II_Cabecera < 0.15
        ) {
            this.colorII = "red";
        } else {
            this.colorII = "gray";
        }
        if (this.mapData.UTE_III_RiosMI >= 0.5) {
            this.colorIII = "yellowGreen";
        } else if (
            this.mapData.UTE_III_RiosMI < 0.5 &&
            this.mapData.UTE_III_RiosMI >= 0.3
        ) {
            this.colorIII = "yellow";
        } else if (
            this.mapData.UTE_III_RiosMI < 0.3 &&
            this.mapData.UTE_III_RiosMI >= 0.15
        ) {
            this.colorIII = "orange";
        } else if (
            this.mapData.UTE_III_RiosMI != null &&
            this.mapData.UTE_III_RiosMI < 0.15
        ) {
            this.colorIII = "red";
        } else {
            this.colorIII = "gray";
        }
        if (this.mapData.UTE_IV_RiosMD >= 0.5) {
            this.colorIV = "yellowGreen";
        } else if (
            this.mapData.UTE_IV_RiosMD < 0.5 &&
            this.mapData.UTE_IV_RiosMD >= 0.3
        ) {
            this.colorIV = "yellow";
        } else if (
            this.mapData.UTE_IV_RiosMD < 0.3 &&
            this.mapData.UTE_IV_RiosMD >= 0.15
        ) {
            this.colorIV = "orange";
        } else if (
            this.mapData.UTE_IV_RiosMD != null &&
            this.mapData.UTE_IV_RiosMD < 0.15
        ) {
            this.colorIV = "red";
        } else {
            this.colorIV = "gray";
        }
        this.legendItems = [
            {
                color: "yellowGreen",
                text: this.$t("droughtIndices.normality").toString()
            },
            {
                color: "yellow",
                text: this.$t("droughtIndices.preAlert").toString()
            },
            {
                color: "orange",
                text: this.$t("droughtIndices.alert").toString()
            },
            {
                color: "red",
                text: this.$t("droughtIndices.emergency").toString()
            },
            { color: "gray", text: this.$t("droughtIndices.noData").toString() }
        ];

        this.updateUnits();
    }

    getDroughtColors() {
        if (
            this.mapData.UTS_I_Principal_Situacion ===
            "Ausencia de sequía prolongada"
        ) {
            this.colorI = "lightSkyBlue";
        } else if (
            this.mapData.UTS_I_Principal_Situacion === "Sequía prolongada"
        ) {
            this.colorI = "coral";
        } else {
            this.colorI = "gray";
        }
        if (
            this.mapData.UTS_II_Cabecera_Situacion ===
            "Ausencia de sequía prolongada"
        ) {
            this.colorII = "lightSkyBlue";
        } else if (
            this.mapData.UTS_II_Cabecera_Situacion === "Sequía prolongada"
        ) {
            this.colorII = "coral";
        } else {
            this.colorII = "gray";
        }
        if (
            this.mapData.UTS_III_RiosMI_Situacion ===
            "Ausencia de sequía prolongada"
        ) {
            this.colorIII = "lightSkyBlue";
        } else if (
            this.mapData.UTS_III_RiosMI_Situacion === "Sequía prolongada"
        ) {
            this.colorIII = "coral";
        } else {
            this.colorIII = "gray";
        }
        if (
            this.mapData.UTS_IV_RiosMD_Situacion ===
            "Ausencia de sequía prolongada"
        ) {
            this.colorIV = "lightSkyBlue";
        } else if (
            this.mapData.UTS_IV_RiosMD_Situacion === "Sequía prolongada"
        ) {
            this.colorIV = "coral";
        } else {
            this.colorIV = "gray";
        }
        this.legendItems = [
            {
                color: "coral",
                text: this.$t("droughtIndices.prolongedDrought").toString()
            },
            {
                color: "lightSkyBlue",
                text: this.$t("droughtIndices.noProlongedDrought").toString()
            },
            { color: "gray", text: this.$t("droughtIndices.noData").toString() }
        ];
        this.updateUnits();
    }

    updateUnits() {
        this.map?.setPaintProperty("zone-i-fill", "fill-color", this.colorI);
        this.map?.setPaintProperty("zone-ii-fill", "fill-color", this.colorII);
        this.map?.setPaintProperty(
            "zone-iii-fill",
            "fill-color",
            this.colorIII
        );
        this.map?.setPaintProperty("zone-iv-fill", "fill-color", this.colorIV);
    }

    /**
     * On Map Loaded
     * @param {MBMap} map Map instance
     * @return {Promise<void>}
     */
    async onMapLoaded(map: MBMap): Promise<void> {
        this.map = map;
        await this.fetchUnits();
        this.drawUnits();
    }

    async fetchUnits() {
        try {
            this.setProgressBar(true);
            const units = await this.$api.getSystemUnits<SystemUnitsResponse>();
            if (units.ok) {
                this.mapFeatures = units.data;
            }
        } catch (error) {
            this.setInfoMessage({
                shown: true,
                text: this.$t("droughtIndices.noData").toString()
            });
        } finally {
            this.setProgressBar(false);
        }
    }

    drawUnits() {
        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: this.mapFeatures.map(unit => {
                return {
                    type: "Feature",
                    geometry: unit.geometry,
                    properties: {
                        name: unit.name,
                        zone: unit.zone,
                        ha: unit.ha
                    }
                };
            })
        };

        const unitSrc: AnySourceImpl | undefined = this.map?.getSource(
            "units-src"
        );

        if (unitSrc) {
            (unitSrc as GeoJSONSource).setData(srcData);
            return;
        }

        this.map?.addSource("units-src", {
            type: "geojson",
            data: srcData
        });

        this.map?.addSource("units-texts", {
            type: "geojson",
            data: {
                type: "FeatureCollection",
                features: [
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [-1.292, 37.9117]
                        },
                        properties: {
                            name: "UTS I - Principal",
                            code: "UTS I"
                        }
                    },
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [-2.2585, 38.3664]
                        },
                        properties: {
                            name: "UTS II - Cabecera",
                            code: "UTS II"
                        }
                    },
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [-1.3751, 38.6182]
                        },
                        properties: {
                            name: "UTS III - Ríos de la margen izquierda",
                            code: "UTS III"
                        }
                    },
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [-2.0122, 37.9604]
                        },
                        properties: {
                            name: "UTS IV - Ríos de la margen derecha",
                            code: "UTS IV"
                        }
                    }
                ]
            }
        });

        this.map?.addLayer({
            id: "zone-i-fill",
            source: "units-src",
            type: "fill",
            filter: ["==", "zone", "I"],
            paint: {
                "fill-color": this.colorI,
                "fill-opacity": 0.4
            }
        });

        this.map?.addLayer({
            id: "zone-i-text",
            source: "units-texts",
            filter: ["==", "code", "UTS I"],
            type: "symbol",
            layout: {
                "text-field": "{name}"
            }
        });

        this.map?.addLayer({
            id: "zone-ii-fill",
            source: "units-src",
            type: "fill",
            filter: ["==", "zone", "II"],
            paint: {
                "fill-color": this.colorII,
                "fill-opacity": 0.4
            }
        });

        this.map?.addLayer({
            id: "zone-ii-text",
            source: "units-texts",
            type: "symbol",
            filter: ["==", "code", "UTS II"],
            layout: {
                "text-field": "{name}"
            }
        });

        this.map?.addLayer({
            id: "zone-iii-fill",
            source: "units-src",
            type: "fill",
            filter: ["==", "zone", "III"],
            paint: {
                "fill-color": this.colorIII,
                "fill-opacity": 0.4
            }
        });

        this.map?.addLayer({
            id: "zone-iii-text",
            source: "units-texts",
            type: "symbol",
            filter: ["==", "code", "UTS III"],
            layout: {
                "text-field": "{name}"
            }
        });

        this.map?.addLayer({
            id: "zone-iv-fill",
            source: "units-src",
            type: "fill",
            filter: ["==", "zone", "IV"],
            paint: {
                "fill-color": this.colorIV,
                "fill-opacity": 0.4
            }
        });

        this.map?.addLayer({
            id: "zone-iv-text",
            source: "units-texts",
            type: "symbol",
            filter: ["==", "code", "UTS IV"],
            layout: {
                "text-field": "{name}"
            }
        });

        this.map?.addLayer({
            id: "units-outline",
            source: "units-src",
            type: "line",
            paint: {
                "line-color": "#000",
                "line-width": 2,
                "line-opacity": 0.4
            }
        });
    }
}
</script>

<style lang="scss" scoped>
.wrap {
    height: 90%;
    height: calc(100vh - 128px);
    width: 100%;
}
</style>
<style></style>
