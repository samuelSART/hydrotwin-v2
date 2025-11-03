<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox :center="mapCenter" :zoom="mapZoom" @loaded="onMapLoaded">
                <template v-slot:form>
                    <HydroEconomicFilterForm
                        v-model="formValues"
                        @on-hydro-economic-filter-updated="
                            onHydroEconomicFilterUpdated
                        "
                    />
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
    DemandUnitIncomeResponse,
    HydroEconomicFilterFormInterface,
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
    income?: number;
}

type MBMouseEvent = MapMouseEvent & {
    features?: MapboxGeoJSONFeature[] | undefined;
} & EventData;

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        HydroEconomicFilterForm: () =>
            import("@/pages/components/forms/HydroEconomicFilterForm.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class HydroEconomic extends Vue {
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

    formValues: HydroEconomicFilterFormInterface = {
        valid: false,
        layer: "agriculture",
        period: "daily"
    };

    legendItems: LegendItem[] = [];

    mouseEventBlocked = false;

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
        this.onHydroEconomicFilterUpdated();
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
     * Get Demand Unit Income
     * @return {Promise<DemandUnitIncomeResponse | undefined>}
     */
    async getDemandUnitIncome(): Promise<DemandUnitIncomeResponse | undefined> {
        const line = window.location.hash
            .replace("#", "")
            .split("/")[1]
            .toUpperCase();
        switch (this.formValues.layer) {
            case "agriculture": {
                return await this.$api.getAgricultureIncome<
                    DemandUnitIncomeResponse
                >(line, this.formValues.period);
            }
            case "urban":
                return await this.$api.getUrbanIncome<DemandUnitIncomeResponse>(
                    line,
                    this.formValues.period
                );
            case "industry":
                return await this.$api.getIndustrialIncome<
                    DemandUnitIncomeResponse
                >(line, this.formValues.period);
            case "golf":
                return await this.$api.getGolfIncome<DemandUnitIncomeResponse>(
                    line,
                    this.formValues.period
                );
            case "wetland":
                return await this.$api.getWetlandIncome<
                    DemandUnitIncomeResponse
                >(line, this.formValues.period);
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
     * @param {void}
     */
    addDemandUnitMouseEvents(): void {
        this.map?.on(
            "mouseenter",
            "demand-units-economy",
            this.handleMouseEnter
        );
        this.map?.on("mousemove", "demand-units-economy", this.handleMouseMove);
        this.map?.on(
            "mouseleave",
            "demand-units-economy",
            this.handleMouseLeave
        );
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

        const info = this.getDemandUnitIncomeDescription(
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

    getDemandUnitIncomeDescription(properties): string {
        let description = `<div>
                <span class="map-waterbody-tooltip">
                ${properties.code}
                </span>
                -
                <span>${properties.name}</span>
            </div>`;

        if (properties.income) {
            description = `${description}
            <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
            <div>
                <span style="font-weight: bold;">${this.$t(
                    "hydroEconomic.income"
                )}:</span> ${properties.income.toFixed(3)} €
            </div>
            `;
        }

        return description;
    }

    /**
     * On Demand Unit Form updated
     * @return {void}
     */
    async onHydroEconomicFilterUpdated(): Promise<void> {
        try {
            this.setProgressBar(true);
            const demandUnitsIncomeResponse = await this.getDemandUnitIncome();

            if (!demandUnitsIncomeResponse || !demandUnitsIncomeResponse.ok) {
                throw new Error("Error getting demand units income");
            }

            const bins = demandUnitsIncomeResponse.data.bins;
            this.legendItems = bins.map((bin, index, elements) => {
                const min = bin === 0 ? 0 : bin.toFixed(2);
                const max = elements[index + 1]
                    ? elements[index + 1].toFixed(2)
                    : "";
                return {
                    color: mapConfig.hydroEconomic.colors[index],
                    text:
                        (min != 0 ? `${min} &lt;` : "") +
                        ` ${this.$t("hydroEconomic.income")} ` +
                        (max != "" ? `&lt; ${max}` : "")
                };
            });
            this.legendItems.unshift({
                color: mapConfig.hydroEconomic.noDataColor,
                text: `0 ${this.$t("hydroEconomic.income")}`
            });

            this.mapSrcData.features.forEach(feature => {
                if (feature.properties?.type === this.formValues.layer) {
                    const demandUnitIncome = demandUnitsIncomeResponse.data.hydroEconomic.find(
                        demandUnitIncome =>
                            demandUnitIncome.code === feature.properties?.code
                    );

                    if (demandUnitIncome && demandUnitIncome.income > 0) {
                        let binIndex = 0;
                        bins.forEach((bin, index) => {
                            if (
                                demandUnitIncome &&
                                demandUnitIncome?.income > bin
                            ) {
                                binIndex = index;
                            }
                        });

                        if (feature && feature.properties) {
                            feature.properties.fillColor =
                                mapConfig.hydroEconomic.colors[binIndex];
                            feature.properties.outlineColor =
                                mapConfig.hydroEconomic.outlineColors[binIndex];
                            feature.properties.income =
                                demandUnitIncome?.income;
                        }
                    } else {
                        feature.properties.income = 0;
                        feature.properties.fillColor =
                            mapConfig.hydroEconomic.noDataColor;
                        feature.properties.outlineColor =
                            mapConfig.hydroEconomic.noDataOutlineColor;
                    }
                }
            });

            (this.map?.getSource("demand-units") as GeoJSONSource).setData(
                this.mapSrcData
            );

            if (this.map?.getLayer("demand-units-economy")) {
                this.map?.removeLayer("demand-units-economy");
            }
            if (this.map?.getLayer("demand-units-economy-outline")) {
                this.map?.removeLayer("demand-units-economy-outline");
            }
            this.map?.off(
                "mouseenter",
                "demand-units-economy",
                this.handleMouseEnter
            );
            this.map?.off(
                "mouseleave",
                "demand-units-economy",
                this.handleMouseLeave
            );

            if (this.formValues.layer === "agriculture") {
                this.map?.addLayer({
                    id: "demand-units-economy",
                    source: "demand-units",
                    type: "fill",
                    paint: {
                        "fill-color": ["get", "fillColor"],
                        "fill-opacity": 0.7
                    },
                    filter: ["==", "$type", "Polygon"]
                });

                this.map?.addLayer({
                    id: "demand-units-economy-outline",
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
                    id: `demand-units-economy`,
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
