<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox :center="mapCenter" :zoom="mapZoom" @loaded="onMapLoaded">
                <template v-slot:form>
                    <CPPiezometerFilterForm
                        v-model="formValues"
                        @on-filter-updated="onFilterUpdated"
                    />
                </template>
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
            <CPPiezometerDialog
                v-model="piezometerDialog.shown"
                :point-info="piezometerDialog.point"
                :variable-code="piezometerDialog.variableCode"
            />
        </div>
    </v-container>
</template>

<script lang="ts">
import {
    AnySourceData,
    GeoJSONSource,
    LngLat,
    LngLatBounds,
    LngLatLike,
    Map as MBMap,
    Popup
} from "mapbox-gl";
import { Component, Vue } from "vue-property-decorator";
import { mapMutations } from "vuex";
import { FeatureCollection, Point } from "geojson";

import {
    MBMouseEvent,
    CPPiezometerResponse,
    CPPiezometer,
    VariableValueResponse,
    VariableValue,
    CPPiezometerForm,
    CPAquifer,
    WaterBodyResponse,
    LegendItem
} from "@/interfaces";
import * as types from "@/store/types";
import {
    cpTimeRangesPieConfig,
    CPTimeRangeConfig,
    cpTimeRangesAqConfig
} from "./cppiezometersconfig";
import { groupBy } from "@/utils";

const PIEZOMETERS_SRC = "piezometers";
const AQUIFERS_SRC = "aquifers";

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        CPPiezometerDialog: () =>
            import("@/components/dialogs/CPPiezometerDialog.vue"),
        CPPiezometerFilterForm: () =>
            import("@/pages/components/forms/CPPiezometerFilterForm.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class CPPiezometers extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    mapCenter: LngLat = new LngLat(-1.136256, 38.076218);
    mapZoom = 8;
    map: MBMap | null = null;
    piezometerDialog = {
        shown: false,
        variableCode: "",
        point: {}
    };
    firstTime = false;
    isUpdatingMap = false;
    piezometers: CPPiezometer[] = [];
    aquifers: CPAquifer[] = [];
    selectedAquiferId: string | number | undefined = undefined;
    selectedPiezometer = false;
    legendItems: LegendItem[] = [];

    popupAquifers = new Popup({
        closeButton: false,
        closeOnClick: false
    });

    formValues: CPPiezometerForm = {
        valid: true,
        timeRange: "latest",
        layerPzmtrs: true,
        layerAqfrs: true
    };

    async onMapLoaded(map: MBMap) {
        this.map = map;

        this.setProgressBar(true);

        // Get all piezometers info and location
        const piezometers = await this.$api
            .getCPPiezometers<CPPiezometerResponse>()
            .catch(() => {
                this.showError(`${this.$t("netError")}`);
            })
            .finally(() => this.setProgressBar(false));

        if (!piezometers || !piezometers.ok) return;

        this.piezometers = piezometers.data;

        this.aquifers = await this.getAquifers(piezometers.data);

        // this.aquifers = this.aquifers.filter(aq => aq.id === "070.010");

        // Draw piezomenters and aquifers state
        this.drawData(this.pieTimeRangeConfig);
    }

    get pieTimeRangeConfig(): CPTimeRangeConfig | undefined {
        return cpTimeRangesPieConfig.find(
            trc => trc.range === this.formValues.timeRange
        );
    }

    get aqTimeRangeConfig(): CPTimeRangeConfig | undefined {
        return cpTimeRangesAqConfig.find(
            trc => trc.range === this.formValues.timeRange
        );
    }

    async drawData(timeRangeConfig: CPTimeRangeConfig | undefined) {
        if (!timeRangeConfig) return;

        this.setProgressBar(true);

        try {
            // Piezometers states
            const piezometersCodes = this.piezometers.map(
                piezometer => piezometer.COD_CHS
            );

            const pnpValues = await this.$api.getCPPiezometersValues<
                VariableValueResponse
            >(piezometersCodes, timeRangeConfig.reqBody);

            if (!pnpValues || !pnpValues.ok) return;

            this.drawPiezometers(
                this.piezometers,
                pnpValues.data,
                timeRangeConfig
            );

            this.drawAquifers(
                this.aquifers,
                pnpValues.data,
                this.aqTimeRangeConfig
            );

            this.legendItems = timeRangeConfig.getLegend
                ? timeRangeConfig.getLegend()
                : [];
        } catch (error) {
            console.error(error);
            this.showError(`${this.$t("netError")}`);
        } finally {
            this.setProgressBar(false);
        }
    }

    drawPiezometers(
        piezometers: CPPiezometer[],
        pnpValues: VariableValue[],
        timeRangeConfig: CPTimeRangeConfig
    ) {
        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: piezometers.map(piezometer => {
                // getting values of variable
                const varPNPValues = pnpValues.filter(
                    lastValVar => lastValVar.variableCode === piezometer.COD_CHS
                );
                const color = timeRangeConfig.computeStateColor(varPNPValues);
                const info = timeRangeConfig.displayInfo
                    ? timeRangeConfig.displayInfo(varPNPValues)
                    : "";

                return {
                    type: "Feature",
                    geometry: piezometer.location,
                    properties: {
                        variableCode: piezometer.COD_CHS,
                        color,
                        measPoint: {
                            denomination: piezometer.MSBT_Nombre,
                            aquifer: piezometer.ACUIFERO,
                            info
                        }
                    }
                };
            })
        };

        /**
         * If mapbox source exists, just update data and return
         */
        const measPontsSrc: AnySourceData | undefined = this.map?.getSource(
            `${PIEZOMETERS_SRC}-src`
        );

        if (measPontsSrc) {
            (measPontsSrc as GeoJSONSource).setData(srcData);
            return;
        }

        /**
         * Create source and layer
         */
        this.map?.addSource(`${PIEZOMETERS_SRC}-src`, {
            type: "geojson",
            data: srcData
        });

        this.map?.addLayer({
            id: `${PIEZOMETERS_SRC}-layer`,
            source: `${PIEZOMETERS_SRC}-src`,
            type: "circle",
            paint: {
                "circle-color": ["get", "color"],
                "circle-stroke-color": "Black",
                "circle-stroke-width": 1
            }
        });

        this.addMouseEvents();
    }

    drawAquifers(
        aquifers: CPAquifer[],
        pnpValues: VariableValue[],
        timeRangeConfig: CPTimeRangeConfig | undefined
    ) {
        if (!timeRangeConfig) return;

        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: aquifers.map(aquifer => {
                // getting values of all piezometers
                const filteredVariables = pnpValues.filter(timeValue =>
                    aquifer.piezometerIds.some(
                        id => id === timeValue.variableCode
                    )
                );

                const color = timeRangeConfig.computeStateColor(
                    filteredVariables
                );
                const info = timeRangeConfig.displayInfo
                    ? timeRangeConfig.displayInfo(
                          filteredVariables,
                          aquifer.piezometerIds.length
                      )
                    : "";

                return {
                    type: "Feature",
                    geometry: aquifer.geometry || {
                        type: "Point",
                        coordinates: [0, 0]
                    },
                    properties: {
                        color,
                        measPoint: {
                            denomination: aquifer.mstb,
                            aquifer: aquifer.name,
                            info
                        }
                    }
                };
            })
        };

        /**
         * If mapbox source exists, just update data and return
         */
        const aquifersPontsSrc: AnySourceData | undefined = this.map?.getSource(
            `${AQUIFERS_SRC}-src`
        );

        if (aquifersPontsSrc) {
            (aquifersPontsSrc as GeoJSONSource).setData(srcData);
            return;
        }

        /**
         * Create source and layer
         */
        this.map?.addSource(`${AQUIFERS_SRC}-src`, {
            type: "geojson",
            data: srcData,
            generateId: true
        });

        this.map?.addLayer(
            {
                id: `${AQUIFERS_SRC}-layer`,
                source: `${AQUIFERS_SRC}-src`,
                type: "fill",
                paint: {
                    "fill-color": ["get", "color"],
                    "fill-opacity": 0.5
                }
            },
            `${PIEZOMETERS_SRC}-layer`
        );

        this.map?.addLayer(
            {
                id: `${AQUIFERS_SRC}-layer-outline`,
                source: `${AQUIFERS_SRC}-src`,
                type: "line",
                layout: {},
                paint: {
                    "line-color": "#000",
                    "line-width": [
                        "case",
                        ["boolean", ["feature-state", "hover"], false],
                        2,
                        1
                    ],
                    "line-opacity": [
                        "case",
                        ["boolean", ["feature-state", "hover"], false],
                        1,
                        0.5
                    ]
                }
            },
            `${PIEZOMETERS_SRC}-layer`
        );

        this.addMouseEventsAquifers();
    }

    async getAquifers(piezometers: CPPiezometer[]): Promise<CPAquifer[]> {
        const aquifersGroups = groupBy(piezometers, "CodMasa");
        const aquifers: CPAquifer[] = [];

        for (const [idAquifer, group] of Object.entries<CPPiezometer[]>(
            aquifersGroups
        )) {
            const piezometers = [...new Set(group.map(g => g.COD_CHS))];
            aquifers.push({
                id: idAquifer,
                name: group[0].ACUIFERO,
                piezometerIds: piezometers,
                mstb: group[0].MSBT_Nombre
            });
        }

        // Get the geometry shape of aquifer searching in water bodies
        const waterBodies = await this.$api.getWaterBodies<WaterBodyResponse>();
        if (!waterBodies || !waterBodies.ok) return [];

        for (const aquifer of aquifers) {
            const wbAq = waterBodies.data.find(wb => wb.code === aquifer.id);
            if (wbAq) {
                aquifer.geometry = wbAq.geometry;
            }
        }

        // return only aquifers with geometry shape
        return aquifers.filter(aq => Boolean(aq.geometry));
    }

    /**
     * Add mouseenter and mouseleave to show popup
     * Add mouseclick to open dialog
     */
    addMouseEvents(): void {
        // Create a popup, but don't add it to the map yet.
        const popup = new Popup({
            closeButton: false,
            closeOnClick: false
        });

        this.map?.on("click", `${PIEZOMETERS_SRC}-layer`, (e: MBMouseEvent) => {
            if (
                !this.map ||
                !e.features ||
                !e.features[0] ||
                !e.features[0].geometry
            )
                return;

            // Copy coordinates array.
            const coordinates = (e.features[0]
                .geometry as Point).coordinates.slice();

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            }

            // Show dialog with info
            const props = e.features[0].properties;
            this.showPiezometerPointData({
                variableCode: props?.variableCode,
                point: JSON.parse(props?.measPoint)
            });
        });

        this.map?.on(
            "mouseenter",
            `${PIEZOMETERS_SRC}-layer`,
            (e: MBMouseEvent) => {
                if (
                    !this.map ||
                    !e.features ||
                    !e.features[0] ||
                    !e.features[0].geometry
                )
                    return;

                this.map.getCanvas().style.cursor = "pointer";

                // Copy coordinates array.
                const coordinates = (e.features[0].geometry as Point)
                    .coordinates;

                // Description
                const info = this.getFeatureDescriptionPiezometer(
                    JSON.parse(e.features[0].properties?.measPoint)
                );

                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] +=
                        e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                popup
                    .setLngLat(coordinates as LngLatLike)
                    .setHTML(info)
                    .addTo(this.map);

                this.selectedPiezometer = true;

                if (this.popupAquifers.isOpen()) this.popupAquifers.remove();
            }
        );

        this.map?.on("mouseleave", `${PIEZOMETERS_SRC}-layer`, () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            popup.remove();

            this.selectedPiezometer = false;
        });
    }

    addMouseEventsAquifers(): void {
        // Create a popup, but don't add it to the map yet.

        this.map?.on(
            "mousemove",
            `${AQUIFERS_SRC}-layer`,
            (e: MBMouseEvent) => {
                if (
                    !this.map ||
                    !e.features ||
                    !e.features[0] ||
                    !e.features[0].geometry ||
                    this.selectedPiezometer
                )
                    return;

                this.map.getCanvas().style.cursor = "pointer";

                // Description
                const info = this.getFeatureDescriptionAquifer(
                    JSON.parse(e.features[0].properties?.measPoint)
                );

                // Populate the popup and set its coordinates
                // based on the feature found.

                if (this.selectedPiezometer && this.popupAquifers.isOpen())
                    this.popupAquifers.remove();

                if (!this.selectedPiezometer) {
                    this.popupAquifers
                        .setLngLat(e.lngLat)
                        .setHTML(info)
                        .addTo(this.map);
                }

                /**
                 * Change line width on hover
                 */
                if (this.selectedAquiferId !== undefined) {
                    this.map.removeFeatureState({
                        source: `${AQUIFERS_SRC}-src`,
                        id: this.selectedAquiferId
                    });
                }

                this.selectedAquiferId = e.features[0].id;

                this.map?.setFeatureState(
                    {
                        source: `${AQUIFERS_SRC}-src`,
                        id: this.selectedAquiferId
                    },
                    {
                        hover: true
                    }
                );
            }
        );

        this.map?.on("mouseleave", `${AQUIFERS_SRC}-layer`, () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            this.popupAquifers.remove();

            if (this.selectedAquiferId !== undefined) {
                this.map.setFeatureState(
                    {
                        source: `${AQUIFERS_SRC}-src`,
                        id: this.selectedAquiferId
                    },
                    {
                        hover: false
                    }
                );
            }
            this.selectedAquiferId = undefined;
        });
    }

    fitMapBounds(coordinates: LngLatLike[]) {
        const bounds = new LngLatBounds(coordinates[0], coordinates[0]);

        // Extend the 'LngLatBounds' to include every coordinate in the bounds result.
        for (const coord of coordinates) {
            bounds.extend(coord);
        }

        this.map?.fitBounds(bounds, {
            padding: 100
        });
    }

    getFeatureDescriptionPiezometer({ info, denomination, aquifer }) {
        return `
            <div class="map-waterbody-tooltip">
                ${this.$t(
                    "CPPiezometer.piezometer"
                )}: ${denomination.toLowerCase()}
            </div>
            <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
            <div>
                ${this.$t("CPPiezometer.aquifer")}: ${aquifer.toLowerCase()}
            </div>
            ${info}
        `;
    }

    getFeatureDescriptionAquifer({ info, denomination, aquifer }) {
        return `
            <div class="map-waterbody-tooltip">
                ${this.$t("CPPiezometer.aquifer")}: ${aquifer.toLowerCase()}
            </div>
            <div>
                mstb: ${denomination.toLowerCase()}
            </div>
            <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
            ${info}
        `;
    }

    /**
     * Show piezometer point data plot
     */
    showPiezometerPointData({ variableCode, point }): void {
        this.piezometerDialog = {
            shown: true,
            variableCode,
            point
        };
    }

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }

    setLayerVisible(idLayer: string, shown: boolean): void {
        const styleValue = shown ? "visible" : "none";
        this.map?.setLayoutProperty(idLayer, "visibility", styleValue);
    }

    /**
     * Filter event
     */
    onFilterUpdated() {
        this.drawData(this.pieTimeRangeConfig);

        this.setLayerVisible(
            `${PIEZOMETERS_SRC}-layer`,
            this.formValues.layerPzmtrs
        );

        this.setLayerVisible(
            `${AQUIFERS_SRC}-layer`,
            this.formValues.layerAqfrs
        );

        this.setLayerVisible(
            `${AQUIFERS_SRC}-layer-outline`,
            this.formValues.layerAqfrs
        );
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
