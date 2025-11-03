<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
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
                                        <div
                                            class="text-caption align-self-center"
                                        >
                                            {{ text }}
                                        </div>
                                    </div>
                                </v-col>
                            </v-row>
                        </v-container>
                    </div>
                </template>
            </MapBox>
            <DamVariablesDialog
                v-model="damVariablesDialog.shown"
                :dam-name="damVariablesDialog.name"
                :dam-code="damVariablesDialog.code"
            />
        </div>
    </v-container>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import { mapMutations } from "vuex";
import {
    Map as MBMap,
    LngLat,
    AnySourceImpl,
    GeoJSONSource,
    MapMouseEvent,
    MapboxGeoJSONFeature,
    EventData,
    Popup
} from "mapbox-gl";
import { FeatureCollection, Geometry } from "geojson";

import {
    Dam,
    DamResponse,
    LegendItem,
    VariableValue,
    VariableValueResponse
} from "@/interfaces";
import * as types from "@/store/types";
import { Timer } from "@/utils/Timer";
import { mapConfig } from "@/config/map";

interface DamPeriod {
    months: [number, number, number];
}

export const DAM_PERIODS = new Map<string, DamPeriod>([
    ["ene_mar", { months: [1, 2, 3] }],
    ["abr_jun", { months: [4, 5, 6] }],
    ["jul_sep", { months: [7, 8, 9] }],
    ["oct_dic", { months: [10, 11, 12] }]
]);

const VOLUME_TYPOLOGY = "V";

interface DamFeature {
    geometry: Geometry;
    code: string;
    name: string;
    color: string;
    outlineColor: string;
    currentVolume: number | string;
    minVolume: number;
    maxVolume: number;
}

type MBMouseEvent = MapMouseEvent & {
    features?: MapboxGeoJSONFeature[] | undefined;
} & EventData;

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        DamVariablesDialog: () =>
            import("@/components/dialogs/DamVariablesDialog.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class Dams extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.136256, 38.12);
    mapZoom = 8;

    dams: Dam[] | undefined = [];
    damFeatures: DamFeature[] | undefined = [];
    selectedDamId: string | number | undefined = undefined;

    timer!: Timer;

    mouseEventBlocked = false;
    damVariablesDialog = {
        shown: false,
        name: "",
        code: ""
    };

    legendItems: LegendItem[] = [
        {
            color: mapConfig.dam.colors.greatherMax,
            text: `${this.$t("dams.legend.greatherMax")}`
        },
        {
            color: mapConfig.dam.colors.betweenMinMax,
            text: `${this.$t("dams.legend.betweenMinMax")}`
        },
        {
            color: mapConfig.dam.colors.lessMin,
            text: `${this.$t("dams.legend.lessMin")}`
        },
        {
            color: mapConfig.dam.colors.noData,
            text: `${this.$t("chart.noData")}`
        }
    ];

    mounted() {
        this.timer = new Timer({
            timeout: mapConfig.dam.timer.timeout,
            immediate: true
        });

        try {
            this.timer.on("tick", async () => {
                try {
                    this.setProgressBar(true);

                    // Get last dams volume data
                    const lastDamsVolume = await this.getLastDamsVolume();

                    if (!lastDamsVolume || !lastDamsVolume.ok) return;

                    // Get dam features and draw them on the map
                    this.damFeatures = await this.getDamsFeatures(
                        lastDamsVolume.data
                    );
                    this.drawDams();
                } catch (error) {
                    console.error(error);
                } finally {
                    this.setProgressBar(false);
                }
            });
        } catch (error) {
            console.error(error);
        }
    }

    destroyed() {
        this.timer.stop();
    }

    /**
     * On Map Loaded
     * @param {MBMap} map Map instance
     * @return {Promise<void>}
     */
    async onMapLoaded(map: MBMap): Promise<void> {
        this.map = map;
        // Get dams
        this.dams = await this.getDams();
        // Start timer
        this.timer.start();
    }

    /**
     * Get dams
     * @return {Promise<Dam[] | undefined>}
     */
    async getDams(): Promise<Dam[] | undefined> {
        try {
            const response = await this.$api.getDamsVariableTypology<
                DamResponse
            >(VOLUME_TYPOLOGY);
            if (!response || !response.ok) return;
            return response.data;
        } catch (error) {
            if (error instanceof Error) {
                if (error.message === "Network Error") {
                    this.showError(String(this.$t("netError")));
                } else {
                    this.showError(error.message);
                }
            }
        }
    }

    /**
     * Get dams features
     * @return {Promise<DamFeature[] | undefine>} Promise with dam features
     */
    async getDamsFeatures(
        lastDamsVolume: VariableValue[]
    ): Promise<DamFeature[] | undefined> {
        // Get current period: ene_mar, abr_jun, jul_sep, oct_dic
        const period = this.getCurrentDatePeriod();

        // Colors
        const colors = mapConfig.dam.colors;
        const outlineColors = mapConfig.dam.outlineColors;

        if (!this.dams || this.dams.length < 0) return;

        const features: DamFeature[] = this.dams.map(dam => {
            let color = colors.noData;
            let outlineColor = outlineColors.noData;

            // Get dam volume last value
            const lastDamVolume:
                | VariableValue
                | undefined = lastDamsVolume.find(
                (damVolume: VariableValue) =>
                    damVolume.variableCode === dam.variable
            );

            if (lastDamVolume) {
                // Convert from Dm3 to hm3
                const currentVolume = lastDamVolume._value / 1000;
                if (currentVolume < dam[`min_${period}`]) {
                    color = colors.lessMin;
                    outlineColor = outlineColors.lessMin;
                } else if (currentVolume > dam[`max_${period}`]) {
                    color = colors.greatherMax;
                    outlineColor = outlineColors.greatherMax;
                } else {
                    color = colors.betweenMinMax;
                    outlineColor = outlineColors.betweenMinMax;
                }
            }

            return {
                geometry: dam.water_body.geometry,
                name: dam.water_body.name,
                code: dam.water_body.code,
                color: color,
                outlineColor: outlineColor,
                currentVolume: lastDamVolume ? lastDamVolume._value / 1000 : "",
                minVolume: dam[`min_${period}`],
                maxVolume: dam[`max_${period}`]
            };
        });

        return features;
    }

    /**
     * Get current period for volume limits
     * @return {string} Month period
     */
    getCurrentDatePeriod(): string {
        let currentPeriod;

        DAM_PERIODS.forEach((period: DamPeriod, key: string) => {
            if (period.months.includes(new Date().getMonth() + 1)) {
                currentPeriod = key;
            }
        });

        return currentPeriod;
    }

    /**
     * Get last volume of dam
     */
    async getLastDamsVolume(): Promise<VariableValueResponse | undefined> {
        // Filter volume variables from dams
        const damsVolumeVariables: Dam[] | undefined = this.dams?.filter(
            dam => {
                if (dam.typology === "V") return dam;
            }
        );

        // Get volumen variables codes
        const variablesCode: string[] | undefined = damsVolumeVariables?.map(
            dam => {
                return dam.variable;
            }
        );

        if (!variablesCode) return;

        return await this.$api.getVariablesLastValues<VariableValueResponse>(
            variablesCode
        );
    }

    /**
     * Draw dams on mapbox
     * @return {void}
     */
    drawDams(): void {
        if (!this.damFeatures || !this.damFeatures.length) return;

        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: this.damFeatures.map(feature => {
                return {
                    type: "Feature",
                    geometry: feature.geometry,
                    properties: {
                        code: feature.code,
                        name: feature.name,
                        color: feature.color,
                        outlineColor: feature.outlineColor,
                        currentVolume: feature.currentVolume,
                        minVolume: feature.minVolume,
                        maxVolume: feature.maxVolume
                    }
                };
            })
        };

        const damSrc: AnySourceImpl | undefined = this.map?.getSource(
            "dams-src"
        );

        if (damSrc) {
            (damSrc as GeoJSONSource).setData(srcData);
            return;
        }

        this.map?.addSource("dams-src", {
            type: "geojson",
            data: srcData,
            generateId: true
        });

        this.map?.addLayer({
            id: "dams-layer",
            source: "dams-src",
            type: "fill",
            paint: {
                "fill-color": ["get", "color"],
                "fill-opacity": 0.75
            }
        });

        this.map?.addLayer({
            id: "dams-layer-outline",
            source: "dams-src",
            type: "line",
            paint: {
                "line-color": [
                    "case",
                    ["boolean", ["feature-state", "hover"], false],
                    "#000",
                    ["get", "outlineColor"]
                ],
                "line-width": 2
            }
        });

        this.addDamMouseEvents();
    }

    /**
     * Add dam mouse events
     * @return {void}
     */
    addDamMouseEvents(): void {
        // Create a popup, but don't add it to the map yet.
        const popup = new Popup({
            closeButton: false,
            closeOnClick: false
        });

        this.map?.on("mousemove", "dams-layer", (e: MBMouseEvent) => {
            if (
                !this.map ||
                this.mouseEventBlocked ||
                !e.features ||
                !e.features[0] ||
                !e.features[0].geometry
            )
                return;

            this.map.getCanvas().style.cursor = "pointer";

            this.selectedDamId = e.features[0].id;

            this.map?.setFeatureState(
                { source: "dams-src", id: e.features[0].id },
                { hover: true }
            );

            const info = this.getDamDescription(e.features[0].properties);

            popup
                .setLngLat(e.lngLat)
                .setHTML(info)
                .addTo(this.map);
        });

        this.map?.on("mouseleave", "dams-layer", () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            if (this.selectedDamId !== undefined) {
                this.map?.setFeatureState(
                    { source: "dams-src", id: this.selectedDamId },
                    { hover: false }
                );
            }
            this.selectedDamId = undefined;

            popup.remove();
        });

        this.map?.on("click", "dams-layer", (e: MBMouseEvent) => {
            if (
                !this.map ||
                !e.features ||
                !e.features[0] ||
                !e.features[0].geometry
            )
                return;

            this.damVariablesDialog = {
                shown: true,
                name: `${e.features[0].properties?.name} (${e.features[0].properties?.code})`,
                code: e.features[0].properties?.code
            };
        });
    }

    getDamDescription(properties): string {
        return `
            <div class="map-waterbody-tooltip">
                ${properties.name} 
                <br/> 
                (${properties.code})
            </div>
            <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
            <div>
                <div>
                    ${this.$t("dams.currentVolume")} (hm<sub>3</sub>):
                    <strong>${properties.currentVolume.toFixed(3)}</strong>
                </div>
            <div>
            <div>
                <div>
                    ${this.$t("dams.minVolume")} (hm<sub>3</sub>):
                    <strong>${properties.minVolume}</strong>
                </div>
            <div>
            <div>
                <div>
                    ${this.$t("dams.maxVolume")} (hm<sub>3</sub>):
                    <strong>${properties.maxVolume}</strong>
                </div>
            <div>
        `;
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
    height: calc(100vh - 128px);
    width: 100%;
}
</style>
<style>
.map-waterbody-tooltip {
    text-align: left;
    font-weight: bold;
}
</style>
