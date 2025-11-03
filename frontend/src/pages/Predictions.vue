<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox
                ref="map-box"
                :center="mapCenter"
                :zoom="mapZoom"
                :drawer="isNotLine1"
                @loaded="onMapLoaded"
                @createPolygon="onCreatePolygon"
                @deletePolygon="onDeletePolygon"
                @updatePolygon="onUpdatePolygon"
            >
                <template v-slot:form>
                    <WMSFilterForm
                        v-model="filterForm"
                        @on-wms-filter-updated="onWMSFilterUpdated"
                    />
                </template>

                <template v-slot:plot>
                    <WMSchart ref="wms-chart" :WMSFilterForm="filterForm" />
                </template>
                <template v-slot:legend>
                    <div>
                        <v-img :src="legendUrl"></v-img>
                    </div>
                </template>
            </MapBox>
        </div>
    </v-container>
</template>

<script lang="ts">
import { Vue, Component, Ref, Prop, Watch } from "vue-property-decorator";
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
import colormap from "colormap";

import {
    DemandUnit,
    DemandUnitResponse,
    DemandUnitRasterStatsResponse,
    WMSFilterFormInterface
} from "@/interfaces";
import { mapConfig } from "@/config/map";
import * as types from "@/store/types";
import WMSchart from "./components/charts/WMSchart.vue";
import MapBox from "@/components/map/MapBox.vue";
import { UDALayerControl } from "@/components/map/MapboxControllers";

interface DemandUnitFeature {
    geometry: Geometry;
    code: string;
    type: string;
    name: string;
    fillColor?: string;
    outlineColor?: string;
    fillOpacity?: number;
    sum?: number;
    mean?: number;
}

type MBMouseEvent = MapMouseEvent & {
    features?: MapboxGeoJSONFeature[] | undefined;
} & EventData;

@Component({
    components: {
        FilterButton: () => import("@/components/layout/FilterButton.vue"),
        WMSFilterForm: () =>
            import("@/pages/components/forms/WMSFilterForm.vue"),
        WMSchart: () => import("@/pages/components/charts/WMSchart.vue"),
        MapBox: () => import("@/components/map/MapBox.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class Predictions extends Vue {
    @Ref("wms-chart") readonly wmsChart!: WMSchart;
    @Ref("map-box") readonly mapBox!: MapBox;
    @Prop({ type: Number, required: false, default: null })
    readonly line!: number;

    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    @Watch("line")
    async onLineUpdate() {
        this.clearMap();
    }

    filterFormPanelShow: boolean | null = false;
    filterForm: WMSFilterFormInterface = {
        valid: false,
        layer: {
            layer: "",
            title: ""
        },
        style: {
            style: "",
            title: ""
        },
        line: this.line,
        selectedDate: new Date().toISOString().split("T")[0]
    };

    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.136256, 38.076218);
    mapZoom = 8;
    wmsUrl = process.env.VUE_APP_WMS_URL || window.location.origin + "/wms";

    demandUnits: DemandUnit[] | undefined = [];
    demandUnitsFeatures: DemandUnitFeature[] | undefined = [];
    selectedDemandUnitId: string | number | undefined = undefined;
    mapUDAControl: UDALayerControl | null = null;
    mouseEventBlocked = false;
    mapSrcData: FeatureCollection = {
        type: "FeatureCollection",
        features: []
    };
    popup: Popup = new Popup({
        closeButton: false,
        closeOnClick: false
    });

    legendUrl: string | null = null;
    legend = document.getElementById("legend");

    drawings: FeatureCollection = {
        type: "FeatureCollection",
        features: []
    };
    drawingCounter = 0;

    get isNotLine1() {
        if (this.line === 1) {
            return false;
        }
        return true;
    }
    /**
     * Methods
     */
    /**
     * On Map Loaded
     * @param {MBMap} map Map instance
     * @return {Promise<void>}
     */
    async onMapLoaded(map: MBMap): Promise<void> {
        this.map = map;
        this.map.addSource("drawings", {
            type: "geojson",
            data: this.drawings
        });
        this.map.addLayer({
            id: "drawing-labels",
            type: "symbol",
            source: "drawings",
            layout: {
                "text-field": ["get", "description"],
                "text-variable-anchor": ["top", "bottom", "left", "right"],
                "text-radial-offset": 1,
                "text-justify": "auto"
            }
        });

        if (this.filterForm.valid) this.onWMSFilterUpdated();
        this.demandUnits = await this.getDemandUnits();
        this.demandUnitsFeatures = await this.getDemandUnitFeatures();
        this.drawDemandUnits();
        this.colorDemandUnits();
        this.mapUDAControl = new UDALayerControl();
        this.map.addControl(this.mapUDAControl, "top-left");
    }

    clearMap(): void {
        this.drawingCounter = 0;
        this.filterForm = {
            valid: false,
            layer: {
                layer: "",
                title: ""
            },
            style: {
                style: "",
                title: ""
            },
            line: this.line,
            selectedDate: new Date().toISOString().split("T")[0]
        };
        this.drawings = {
            type: "FeatureCollection",
            features: []
        };
        if (this.map?.getLayer("prediction")) {
            this.map?.removeLayer("prediction");
        }
        if (this.map?.getSource("wms")) {
            this.map?.removeSource("wms");
        }
        if (this.map?.getSource("drawings")) {
            (this.map?.getSource("drawings") as GeoJSONSource).setData(
                this.drawings
            );
        }
        this.mapBox.removeAllDraws();
        this.wmsChart.deleteAll();
    }
    /**
     * Get Demand Units
     * @return {Promise<DemandUnit[] | undefined>}
     */
    async getDemandUnits(): Promise<DemandUnit[] | undefined> {
        try {
            this.setProgressBar(true);
            const response = await this.$api.getDemandUnits<DemandUnitResponse>(
                "agriculture"
            );
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
     * On Demand Unit Form updated
     * @return {void}
     */
    async colorDemandUnits(): Promise<void> {
        try {
            this.setProgressBar(true);
            const demandUnitStats = await this.$api.getDemandUnitRasterStats<
                DemandUnitRasterStatsResponse
            >(this.filterForm.selectedDate, this.filterForm.layer.layer);

            if (!demandUnitStats || !demandUnitStats.ok) {
                throw new Error("Error getting demand units stats");
            }

            let colors: colormap | undefined = undefined;
            if (
                this.filterForm.layer.layer == "evapotranspiration" ||
                this.filterForm.layer.layer == "evapotranspiration_monthly"
            ) {
                colors = colormap({
                    colormap: "winter",
                    nshades: 100,
                    format: "hex",
                    alpha: 1
                });
            } else if (
                this.filterForm.layer.layer == "waterdemand" ||
                this.filterForm.layer.layer == "waterdemand_monthly"
            ) {
                colors = colormap({
                    colormap: "summer",
                    nshades: 60,
                    format: "hex",
                    alpha: 1
                });
            } else if (this.filterForm.layer.layer == "biomass") {
                colors = colormap({
                    colormap: "summer",
                    nshades: 10000,
                    format: "hex",
                    alpha: 1
                });
            }
            const demandUnitStatsData = demandUnitStats.data.values;
            this.mapSrcData.features.forEach(feature => {
                if (demandUnitStatsData) {
                    const demandUnitStat =
                        demandUnitStatsData[feature.properties?.code];
                    if (demandUnitStat) {
                        if (feature && feature.properties) {
                            feature.properties.sum = demandUnitStat.sum;
                            feature.properties.mean = demandUnitStat.mean;
                            if (colors != undefined) {
                                feature.properties.fillColor =
                                    colors[
                                        Math.round(10 * demandUnitStat.mean)
                                    ];
                            } else {
                                feature.properties.fillColor =
                                    mapConfig.rasterUDAStats.noDataColor;
                            }
                            feature.properties.outlineColor =
                                mapConfig.rasterUDAStats.outlineColor;
                            feature.properties.fillOpacity = 0.8;
                        }
                    } else {
                        if (feature && feature.properties) {
                            feature.properties.mean = "No data";
                            feature.properties.sum = "No data";
                            feature.properties.fillColor =
                                mapConfig.rasterUDAStats.noDataColor;
                            feature.properties.outlineColor =
                                mapConfig.rasterUDAStats.noDataOutlineColor;
                            feature.properties.fillOpacity = 0.05;
                        }
                    }
                } else {
                    if (feature && feature.properties) {
                        feature.properties.mean = "No data";
                        feature.properties.sum = "No data";
                        feature.properties.fillColor =
                            mapConfig.hydroEconomic.noDataColor;
                        feature.properties.outlineColor =
                            mapConfig.hydroEconomic.noDataOutlineColor;
                        feature.properties.fillOpacity = 0.05;
                    }
                }
            });

            if (this.map?.getSource("demand-units")) {
                (this.map?.getSource("demand-units") as GeoJSONSource).setData(
                    this.mapSrcData
                );
            } else {
                console.log("No demand units");
                return;
            }

            let visibility = "none";
            if (this.map?.getLayer("demand-units-stats")) {
                visibility = this.map?.getLayoutProperty(
                    "demand-units-stats",
                    "visibility"
                );
                this.map?.removeLayer("demand-units-stats");
            }
            if (this.map?.getLayer("demand-units-stats-outline")) {
                this.map?.removeLayer("demand-units-stats-outline");
            }
            this.map?.off(
                "mouseenter",
                "demand-units-stats",
                this.handleMouseEnter
            );
            this.map?.off(
                "mouseleave",
                "demand-units-stats",
                this.handleMouseLeave
            );

            this.map?.addLayer({
                id: "demand-units-stats",
                source: "demand-units",
                type: "fill",
                paint: {
                    "fill-color": ["get", "fillColor"],
                    "fill-opacity": ["get", "fillOpacity"]
                },
                filter: ["==", "$type", "Polygon"]
            });

            this.map?.addLayer({
                id: "demand-units-stats-outline",
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
            this.map?.setLayoutProperty(
                "demand-units-stats",
                "visibility",
                visibility
            );
            this.map?.setLayoutProperty(
                "demand-units-stats-outline",
                "visibility",
                visibility
            );

            this.addDemandUnitMouseEvents();
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
     * Add Demand Unit Mouse Events
     * @param {void}
     */
    addDemandUnitMouseEvents(): void {
        this.map?.on("mouseenter", "demand-units-stats", this.handleMouseEnter);
        this.map?.on("mousemove", "demand-units-stats", this.handleMouseMove);
        this.map?.on("mouseleave", "demand-units-stats", this.handleMouseLeave);
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

        const info = this.getDemandUnitDescription(e.features[0].properties);

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

    onCreatePolygon(e): void {
        const feature = e.features[0];
        this.drawingCounter += 1;
        feature.properties.description = "G " + this.drawingCounter;
        this.drawings.features.push(feature);
        if (this.map?.getSource("drawings")) {
            (this.map.getSource("drawings") as GeoJSONSource).setData(
                this.drawings
            );
        }
        this.wmsChart.onCreatePolygon(feature);
    }

    onDeletePolygon(e): void {
        const id = e.features[0].id;
        const feature = this.findDrawing(id);
        if (feature) {
            const featureId = feature.properties?.description;
            this.drawings.features?.splice(
                this.drawings.features.indexOf(feature),
                1
            );
            if (this.map?.getSource("drawings")) {
                (this.map.getSource("drawings") as GeoJSONSource).setData(
                    this.drawings
                );
            }
            this.wmsChart.onDeletePolygon(featureId);
        }
    }

    onUpdatePolygon(e): void {
        const feature = e.features[0];
        const id = feature.id;
        const oldFeature = this.findDrawing(id);
        if (oldFeature) {
            const description = oldFeature.properties?.description;
            feature.properties.description = description;
            this.drawings.features.splice(
                this.drawings.features.indexOf(oldFeature),
                1
            );
            this.drawings.features.push(feature);
            if (this.map?.getSource("drawings")) {
                (this.map.getSource("drawings") as GeoJSONSource).setData(
                    this.drawings
                );
            }
            this.wmsChart.onUpdatePolygon(feature);
        }
    }

    findDrawing(id: string) {
        const found = this.drawings.features.find(feature => feature.id === id);
        return found;
    }

    loadWMS(layer: string, style: string, time: string): void {
        if (this.map?.getLayer("prediction")) {
            this.map?.removeLayer("prediction");
        }
        if (this.map?.getSource("wms")) {
            this.map?.removeSource("wms");
        }

        this.map?.addSource("wms", {
            type: "raster",
            tiles: [
                `${this.wmsUrl}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=${layer}&STYLES=${style}&TIME=${time}T10:00:00&FORMAT=image/png&CRS=EPSG:3857&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE&WIDTH=256&HEIGHT=256&BBOX={bbox-epsg-3857}`
            ],
            tileSize: 256
        });
        this.map?.addLayer({
            id: "prediction",
            type: "raster",
            source: "wms",
            paint: {
                "raster-opacity": 0.65
            }
        });
        this.legendUrl = `${this.wmsUrl}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetLegendGraphic&LAYER=${this.filterForm.layer.layer}&STYLES=${this.filterForm.style.style}&FORMAT=image/png`;
    }

    onWMSFilterUpdated(): void {
        this.loadWMS(
            this.filterForm.layer.layer,
            this.filterForm.style.style,
            this.filterForm.selectedDate
        );
        console.log("Reload WMS");
        this.colorDemandUnits();
    }

    getDemandUnitDescription(properties): string {
        let description = `<div>
                <span class="map-waterbody-tooltip">
                ${properties.code}
                </span>
                -
                <span>${properties.name}</span>
            </div>`;

        let sum = "No data";
        let mean = "No data";
        let unit1 = "";
        let unit2 = "";
        if (
            this.filterForm.layer.layer == "evapotranspiration" ||
            this.filterForm.layer.layer == "waterdemand"
        ) {
            unit1 = `mm ${this.$t("daily")}`;
            unit2 = `m³ ${this.$t("daily")}`;
        } else if (
            this.filterForm.layer.layer == "evapotranspiration_monthly" ||
            this.filterForm.layer.layer == "waterdemand_monthly"
        ) {
            unit1 = `mm ${this.$t("monthly")}`;
            unit2 = `m³ ${this.$t("monthly")}`;
        } else if (this.filterForm.layer.layer == "biomass") {
            unit1 = "g/m²";
            unit2 = "kg";
        }
        if (properties.mean > -1) {
            mean = properties.mean.toFixed(3);
            sum = properties.sum.toFixed(3);
        }
        description = `${description}
        <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
        <div>
            <span style="font-weight: bold;">${this.$t(
                `WMSFilterForm.${this.filterForm.layer.layer}`
            )}:</span> (${this.filterForm.selectedDate})
            <br>
            ${this.$t("mean")}: ${mean} ${unit1}
            <br>
            ${this.$t("sum")}: ${sum} ${unit2}
        </div>
        `;

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
<style lang="scss">
.centered-input input {
    text-align: center;
}
</style>
