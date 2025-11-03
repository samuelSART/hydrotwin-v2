<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox :center="mapCenter" :zoom="mapZoom" @loaded="onMapLoaded">
                <template v-slot:form>
                    <CO2FilterForm
                        v-model="formValues"
                        @on-co2-filter-updated="onCO2FilterUpdated"
                    />
                </template>
                <template v-slot:info>
                    <div class="pa-2" v-if="demandEmission && waterEmission">
                        <v-container>
                            <v-row>
                                <div class="font-weight-bold">
                                    <span v-html="$t('CO2.resumenCO2')"></span>
                                </div>
                            </v-row>
                            <v-row>
                                <div class="text-caption">
                                    {{ $t("CO2.perDemandUnit") }}:
                                    {{ getDemandEmission }}
                                    t CO<sub>2</sub>
                                </div>
                            </v-row>
                            <v-row>
                                <div class="text-caption">
                                    {{ $t("CO2.perWaterUse") }}:
                                    {{ getWaterEmission }}
                                    t CO<sub>2</sub>
                                </div>
                            </v-row>
                        </v-container>
                    </div>
                </template>
                <template v-slot:legend>
                    <div class="pa-2" v-if="legendItems.length">
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
                                            v-html="text"
                                        ></div>
                                    </div>
                                </v-col>
                            </v-row>
                        </v-container>
                    </div>
                </template>
            </MapBox>
        </div>
    </v-container>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import { mapMutations } from "vuex";
import {
    Map as MBMap,
    LngLat,
    MapMouseEvent,
    MapboxGeoJSONFeature,
    EventData,
    AnySourceImpl,
    GeoJSONSource,
    Popup
} from "mapbox-gl";
import { FeatureCollection, Geometry } from "geojson";

import * as types from "@/store/types";
import {
    DemandUnit,
    DemandUnitResponse,
    DemandUnitEmissionsResponse,
    CO2FilterFormInterface,
    LegendItem
} from "@/interfaces";
import { mapConfig } from "@/config/map";

interface DemandUnitFeature {
    geometry: Geometry;
    code: string;
    type: string;
    name: string;
    fillColor?: string;
    outlineColor?: string;
}

export const DEMAND_UNIT_COLORS = new Map<string, string>([
    ["urban", "#F08080"],
    ["industry", "#A0522D"],
    ["golf", "#8FBC8F"],
    ["wetland", "#D2B48C"]
]);

type MBMouseEvent = MapMouseEvent & {
    features?: MapboxGeoJSONFeature[] | undefined;
} & EventData;

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        CO2FilterForm: () =>
            import("@/pages/components/forms/CO2FilterForm.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class CO2 extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.136256, 38.12);
    mapZoom = 8;
    mapSrcData: FeatureCollection = {
        type: "FeatureCollection",
        features: []
    };
    popup: Popup = new Popup({
        closeButton: false,
        closeOnClick: false
    });

    demandUnits: DemandUnit[] | undefined = [];
    demandUnitsFeatures: DemandUnitFeature[] | undefined = [];
    selectedDemandUnitId: string | number | undefined = undefined;

    demandEmission: number | null = null;
    waterEmission: number | null = null;

    formValues: CO2FilterFormInterface = {
        valid: false,
        layer: "agriculture",
        period: "daily"
    };

    legendItems: LegendItem[] = [];

    mouseEventBlocked = false;

    /**
     * Computed properties
     */
    get getDemandEmission() {
        if (this.demandEmission) {
            return this.demandEmission.toFixed(2);
        }
        return "";
    }

    get getWaterEmission() {
        if (this.waterEmission) {
            return this.waterEmission.toFixed(2);
        }
        return "";
    }

    /**
     * On Map Loaded
     * @param {MBMap} map Map instance
     * @return {Promise<void>}
     */
    async onMapLoaded(map: MBMap): Promise<void> {
        this.map = map;
        this.demandUnits = await this.getDemandUnits();
        this.demandUnitsFeatures = await this.getDemandUnitFeatures();
        this.drawDemandUnits();
        this.onCO2FilterUpdated();
    }

    /**
     * Get Demand Units
     * @return {Promise<DemandUnit[] | undefined>}
     */
    async getDemandUnits(): Promise<DemandUnit[] | undefined> {
        try {
            this.setProgressBar(true);
            const response = await this.$api.getDemandUnits<
                DemandUnitResponse
            >();
            if (!response || !response.ok) return;
            return response.data;
        } catch (error) {
            console.error(error);
        } finally {
            this.setProgressBar(false);
        }
    }

    /**
     * Get Demand Unit Features
     * @return {Promise<DemandUnitFeature[] | undefined>}
     */
    async getDemandUnitFeatures(): Promise<DemandUnitFeature[] | undefined> {
        if (!this.demandUnits || !this.demandUnits.length) return;

        const features: DemandUnitFeature[] = this.demandUnits?.map(
            demandUnit => {
                return {
                    geometry: demandUnit.geometry,
                    code: demandUnit.code,
                    type: demandUnit.type,
                    name: demandUnit.name
                };
            }
        );
        return features;
    }

    /**
     * Get Demand Unit Emissions
     * @return {Promise<DemandUnitEmissionsResponse> | undefined}
     */
    async getDemandUnitEmissions(): Promise<
        DemandUnitEmissionsResponse | undefined
    > {
        const line = window.location.hash
            .replace("#", "")
            .split("/")[1]
            .toUpperCase();
        switch (this.formValues.layer) {
            case "agriculture":
                return await this.$api.getAgricultureEmissions<
                    DemandUnitEmissionsResponse
                >(this.formValues.period, line);
            case "urban":
                return await this.$api.getUrbanEmissions<
                    DemandUnitEmissionsResponse
                >(this.formValues.period, line);
            case "industry":
                return await this.$api.getIndustrialEmissions<
                    DemandUnitEmissionsResponse
                >(this.formValues.period, line);
            case "golf":
                return await this.$api.getGolfEmissions<
                    DemandUnitEmissionsResponse
                >(this.formValues.period, line);
            case "wetland":
                return await this.$api.getWetlandEmissions<
                    DemandUnitEmissionsResponse
                >(this.formValues.period, line);
            default:
                return;
        }
    }

    /**
     * Draw demands units
     * @return {void}
     */
    drawDemandUnits(): void {
        if (!this.demandUnitsFeatures || !this.demandUnitsFeatures.length)
            return;

        this.mapSrcData = {
            type: "FeatureCollection",
            features: this.demandUnitsFeatures.map(feature => {
                return {
                    type: "Feature",
                    geometry: feature.geometry,
                    properties: {
                        code: feature.code,
                        name: feature.name,
                        type: feature.type
                    }
                };
            })
        };

        const demandUnitSrc: AnySourceImpl | undefined = this.map?.getSource(
            "demand-units"
        );

        if (demandUnitSrc) {
            (demandUnitSrc as GeoJSONSource).setData(this.mapSrcData);
            return;
        }

        this.map?.addSource("demand-units", {
            type: "geojson",
            data: this.mapSrcData,
            generateId: true
        });
    }

    /**
     * Add Demand Unit Mouse Events
     * @return {void}
     */
    addDemandUnitMouseEvents(): void {
        this.map?.on("mouseenter", "demand-units-co2", this.handleMouseEnter);
        this.map?.on("mousemove", "demand-units-co2", this.handleMouseMove);
        this.map?.on("mouseleave", "demand-units-co2", this.handleMouseLeave);
    }

    /**
     * Handle Mouse Enter
     * @param {MBMouseEvent} e
     * @return {void}
     */
    handleMouseEnter(e: MBMouseEvent): void {
        if (
            !this.map ||
            this.mouseEventBlocked ||
            !e.features ||
            !e.features[0] ||
            !e.features[0].geometry
        )
            return;

        this.map.getCanvas().style.cursor = "pointer";
    }

    /**
     * Handle Mouse Move
     * @param {MBMouseEvent} e
     * @return {void}
     */
    handleMouseMove(e: MBMouseEvent): void {
        if (
            !this.map ||
            this.mouseEventBlocked ||
            !e.features ||
            !e.features[0] ||
            !e.features[0].geometry
        )
            return;

        this.map.getCanvas().style.cursor = "pointer";

        if (this.selectedDemandUnitId !== undefined) {
            this.map.removeFeatureState({
                source: "demand-units",
                id: this.selectedDemandUnitId
            });
        }

        this.selectedDemandUnitId = e.features[0].id;

        this.map?.setFeatureState(
            { source: "demand-units", id: e.features[0].id },
            { hover: true }
        );

        const info = this.getDemandUnitEmissionsDescription(
            e.features[0].properties
        );

        this.popup
            .setLngLat(e.lngLat)
            .setHTML(info)
            .addTo(this.map);
    }

    /**
     * Handle Mouse Leave
     * @return {void}
     */
    handleMouseLeave(): void {
        if (!this.map) return;

        this.map.getCanvas().style.cursor = "";
        if (this.selectedDemandUnitId !== undefined) {
            this.map?.setFeatureState(
                { source: "demand-units", id: this.selectedDemandUnitId },
                { hover: false }
            );
        }
        this.selectedDemandUnitId = undefined;

        this.popup.remove();
    }

    /**
     * On Demand Unit Form updated
     * @return {void}
     */
    async onCO2FilterUpdated(): Promise<void> {
        try {
            this.setProgressBar(true);
            const emissionsResponse = await this.getDemandUnitEmissions();

            if (!emissionsResponse || !emissionsResponse.ok) {
                throw new Error("Error getting CO2 emissions");
            }

            this.demandEmission = emissionsResponse.data.emissions.reduce(
                function(acc, item) {
                    return acc + item.demand;
                },
                0
            );
            this.demandEmission.toFixed(3);

            this.waterEmission = emissionsResponse.data.emissions.reduce(
                function(acc, item) {
                    return acc + item.water.total;
                },
                0
            );
            this.waterEmission.toFixed(3);

            const bins = emissionsResponse.data.bins;
            this.legendItems = bins.map((bin, index, elements) => {
                return {
                    color: mapConfig.co2.colors[index],
                    text:
                        String(bin.toFixed(3)) +
                        " &lt; t CO<sub>2</sub>" +
                        (elements[index + 1]
                            ? " &le; " + String(elements[index + 1]?.toFixed(3))
                            : "")
                };
            });

            this.mapSrcData.features.forEach(feature => {
                if (feature.properties?.type === this.formValues.layer) {
                    const demandUnitEmission = emissionsResponse.data.emissions.find(
                        emission => emission.code === feature.properties?.code
                    );

                    let binIndex = 0;
                    bins.forEach((bin, index) => {
                        if (
                            demandUnitEmission &&
                            demandUnitEmission?.total > bin
                        ) {
                            binIndex = index;
                        }
                    });

                    if (feature && feature.properties) {
                        feature.properties.fillColor =
                            mapConfig.co2.colors[binIndex];
                        feature.properties.outlineColor =
                            mapConfig.co2.outlineColors[binIndex];
                        feature.properties.emissions =
                            demandUnitEmission?.total;
                        feature.properties.demand = demandUnitEmission?.demand;
                        feature.properties.water = demandUnitEmission?.water;
                    }
                }
            });

            (this.map?.getSource("demand-units") as GeoJSONSource).setData(
                this.mapSrcData
            );

            if (this.map?.getLayer("demand-units-co2")) {
                this.map?.removeLayer("demand-units-co2");
            }
            if (this.map?.getLayer("demand-units-co2-outline")) {
                this.map?.removeLayer("demand-units-co2-outline");
            }
            this.map?.off(
                "mouseenter",
                "demand-units-co2",
                this.handleMouseEnter
            );
            this.map?.off(
                "mouseleave",
                "demand-units-co2",
                this.handleMouseLeave
            );

            if (this.formValues.layer === "agriculture") {
                this.map?.addLayer({
                    id: "demand-units-co2",
                    source: "demand-units",
                    type: "fill",
                    paint: {
                        "fill-color": ["get", "fillColor"],
                        "fill-opacity": 0.7
                    },
                    filter: ["==", "$type", "Polygon"]
                });

                this.map?.addLayer({
                    id: "demand-units-co2-outline",
                    source: "demand-units",
                    type: "line",
                    paint: {
                        "line-color": [
                            "case",
                            ["boolean", ["feature-state", "hover"], false],
                            "#000",
                            ["get", "outlineColor"]
                        ],
                        "line-width": 1
                    },
                    filter: ["==", "$type", "Polygon"]
                });

                this.addDemandUnitMouseEvents();
            } else {
                this.map?.addLayer({
                    id: `demand-units-co2`,
                    source: "demand-units",
                    type: "circle",
                    paint: {
                        "circle-radius": 6,
                        "circle-color": ["get", "fillColor"]
                    },
                    filter: [
                        "all",
                        ["==", "$type", "Point"],
                        ["==", "type", this.formValues.layer]
                    ]
                });

                this.addDemandUnitMouseEvents();
            }
        } catch (error) {
            if (error instanceof Error) {
                if (error.message === "Network Error") {
                    this.showError(String(this.$t("netError")));
                } else {
                    this.showError(error.message);
                }
            }
        } finally {
            this.setProgressBar(false);
        }
    }

    /**
     * Get Demand Unit Emissions
     * @param {GeoJsonProperties} properties
     * @return {Promise<AxiosResponse<any>>}
     */
    getDemandUnitEmissionsDescription(properties): string {
        let description = `<div>
                <span class="map-waterbody-tooltip">
                ${properties.code}
                </span>
                -
                <span>${properties.name}</span>
            </div>`;

        if (
            properties.emissions > 0 ||
            properties.demand > 0 ||
            properties.water > 0
        ) {
            description = `${description}
                <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">`;
        }
        if (properties.emissions) {
            description = `${description}
                <div>
                    <span style="font-weight: bold;">Total Emissions:</span> ${properties.emissions.toFixed(
                        3
                    )} t CO<sub>2</sub>
                </div>
        `;
        }
        if (properties.demand) {
            description = `${description}
                <div>
                    <span style="font-weight: bold;">Demand Emissions:</span> ${properties.demand.toFixed(
                        3
                    )} t CO<sub>2</sub>
                </div>
        `;
        }
        if (properties.water) {
            description = `${description}
                <div>
                    <span style="font-weight: bold;">Water Emissions:</span> ${properties.water.toFixed(
                        3
                    )} t CO<sub>2</sub>
                </div>
        `;
        }
        return description;
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
    text-align: center;
    font-weight: bold;
}
</style>
