<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox
                :center="mapCenter"
                :zoom="mapZoom"
                :mapImages="mapImages"
                :mapBounds="mapBounds"
                @loaded="onMapLoaded"
            />
            <SaicaDialog
                v-model="measPointDialog.shown"
                :point-info="measPointDialog.point"
                :variable-code="measPointDialog.variableCode"
            />
        </div>
    </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import {
    Map as MBMap,
    LngLat,
    AnySourceData,
    GeoJSONSource,
    LngLatLike,
    Popup
} from "mapbox-gl";
import { FeatureCollection, Point } from "geojson";
import { mapMutations } from "vuex";

import {
    MeasurementPointResponse,
    MeasurementPoint,
    Variable,
    VariableValueResponse,
    VariableValue,
    MBMouseEvent
} from "@/interfaces";
import { MapImageDef } from "@/components/map/MapBox.vue";
import { Timer } from "@/utils/Timer";
import { mapConfig } from "@/config/map";
import * as types from "@/store/types";

const MEASPOINTS_SRC = "MeasPoints";
const MEASPOINT_ICON_DEFAULT = "measpoint_default";
const MAP_IMAGES: MapImageDef[] = [
    {
        url: require("@/assets/img/measpoint.png"),
        id: MEASPOINT_ICON_DEFAULT
    }
];

interface MeasPointVarValue extends Variable {
    latestValue?: Partial<VariableValue>;
}

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        SaicaDialog: () => import("@/components/dialogs/SaicaDialog.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class QualitySaica extends Vue {
    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.136256, 38.076218);
    mapZoom = 8;
    mapImages = Object.freeze(MAP_IMAGES);
    timer!: Timer;
    isUpdatingMap = false;
    mapBounds: LngLatLike[] = [];
    firstTime = true;

    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    measPointDialog = {
        shown: false,
        variableCode: "",
        point: {}
    };

    mounted() {
        this.timer = new Timer({
            timeout: mapConfig.saica.timer.timeout,
            immediate: true
        });

        this.timer.on("tick", async () => {
            try {
                if (this.isUpdatingMap) return undefined;
                this.isUpdatingMap = true;

                this.setProgressBar(true);

                const measPointsResponse = await this.$api.getMeasurementPoints<
                    MeasurementPointResponse
                >({ typology: ["Q"] });

                if (measPointsResponse && measPointsResponse.ok) {
                    const latestMeasPointValues = new Map<
                        string,
                        MeasPointVarValue[]
                    >();
                    const measPoints = measPointsResponse.data;

                    /**
                     * Foreach variable of each meas point get the latest value
                     * and save it into map
                     */
                    for (const mPoint of measPoints) {
                        const measVarCodes = mPoint.variables.map(v => v.code);
                        const latestValuesRes = await this.$api.getVariablesLastValues<
                            VariableValueResponse
                        >(measVarCodes);
                        const latestValues = latestValuesRes.data;

                        latestMeasPointValues.set(mPoint.code, [
                            ...mPoint.variables.map(variable => {
                                const latestValue = latestValues.find(
                                    lv => lv.variableCode === variable.code
                                );
                                return {
                                    ...variable,
                                    latestValue: {
                                        _time: latestValue?._time,
                                        _value: latestValue?._value
                                    }
                                };
                            })
                        ]);
                    }

                    this.drawMeasurementPoints(
                        measPointsResponse.data,
                        latestMeasPointValues
                    );

                    // Fit bounds
                    if (!this.firstTime) return;
                    this.firstTime = false;

                    this.mapBounds = measPoints.map(piezometer => {
                        const point = piezometer.location as Point;
                        return point.coordinates as LngLatLike;
                    });
                }
            } catch (error) {
                console.error("[quality saica]", error);
                this.showError(`${this.$t("netError")}`);
            } finally {
                this.setProgressBar(false);
                this.isUpdatingMap = false;
            }
        });
    }

    destroyed() {
        this.timer.stop();
    }

    async onMapLoaded(map: MBMap) {
        this.map = map;
        this.timer.start();
    }

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }

    drawMeasurementPoints(
        measPoints: MeasurementPoint[],
        latestMeasPointValues: Map<string, MeasPointVarValue[]>
    ) {
        if (!measPoints.length) return;

        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: measPoints.map(measPoint => {
                return {
                    type: "Feature",
                    geometry: measPoint.location,
                    properties: {
                        code: measPoint.code,
                        measPoint: {
                            denomination: measPoint.denomination,
                            description: measPoint.description,
                            typology: measPoint.typology,
                            variables: latestMeasPointValues.get(measPoint.code)
                        }
                    }
                };
            })
        };

        /**
         * If mapbox source exists, just update data and return
         */
        const measPontsSrc: AnySourceData | undefined = this.map?.getSource(
            `${MEASPOINTS_SRC}-src`
        );

        if (measPontsSrc) {
            (measPontsSrc as GeoJSONSource).setData(srcData);
            return;
        }

        /**
         * Create source and layer
         */
        this.map?.addSource(`${MEASPOINTS_SRC}-src`, {
            type: "geojson",
            data: srcData,
            cluster: false
        });

        this.map?.addLayer({
            id: `${MEASPOINTS_SRC}-layer`,
            source: `${MEASPOINTS_SRC}-src`,
            type: "symbol",
            layout: {
                "icon-image": MEASPOINT_ICON_DEFAULT,
                "icon-size": 1,
                "icon-allow-overlap": true
            }
        });

        this.addMouseEvents();
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

        this.map?.on("click", `${MEASPOINTS_SRC}-layer`, (e: MBMouseEvent) => {
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
            this.showMeasPointData({
                variableCode: props?.code,
                point: JSON.parse(props?.measPoint)
            });
        });

        this.map?.on(
            "mouseenter",
            `${MEASPOINTS_SRC}-layer`,
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
                const props = e.features[0].properties;
                let info = "";
                if (props) {
                    info = this.getFeatureDescription(
                        JSON.parse(props.measPoint)
                    );
                }

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
            }
        );

        this.map?.on("mouseleave", `${MEASPOINTS_SRC}-layer`, () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            popup.remove();
        });
    }

    getFeatureDescription({
        denomination,
        variables
    }: {
        denomination: string;
        variables: MeasPointVarValue[];
    }) {
        const variablesValues = variables
            .map(v => {
                const lValue = v.latestValue?._value ?? "--";

                return `
                    <div>
                        ${v.description}: <strong>${lValue}</strong>
                    </div>
                `;
            })
            .join("");

        return `
            <div class="map-waterbody-tooltip">
                ${denomination}
            </div>
            <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
            <div>
                ${variablesValues}
            </div>
        `;
    }

    /**
     * Show measpoint point data plot
     */
    showMeasPointData({ variableCode, point }): void {
        this.measPointDialog = {
            shown: true,
            variableCode,
            point
        };
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
