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
            <PiezometerDialog
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
    LngLatLike,
    Map as MBMap,
    Popup
} from "mapbox-gl";
import { Component, Vue } from "vue-property-decorator";
import { mapMutations } from "vuex";
import { FeatureCollection, Point } from "geojson";

import {
    MBMouseEvent,
    MeasurementPoint,
    MeasurementPointResponse
} from "@/interfaces";
import { MapImageDef } from "@/components/map/MapBox.vue";
import * as types from "@/store/types";
import { sleep } from "@/utils";
import { Timer } from "@/utils/Timer";
import { mapConfig } from "@/config/map";

const PIEZOMETERS_SRC = "piezometers";
const PIEZOMETER_ICON_DEFAULT = "piezometer_default";
const MAP_IMAGES: MapImageDef[] = [
    {
        url: require("@/assets/img/piezometer.png"),
        id: PIEZOMETER_ICON_DEFAULT
    }
];

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        PiezometerDialog: () =>
            import("@/components/dialogs/PiezometerDialog.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class Piezometers extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    mapCenter: LngLat = new LngLat(-1.136256, 38.076218);
    mapZoom = 8;
    map: MBMap | null = null;
    timer!: Timer;
    piezometerDialog = {
        shown: false,
        variableCode: "",
        point: {}
    };
    mapImages = Object.freeze(MAP_IMAGES);
    firstTime = true;
    isUpdatingMap = false;
    mapBounds: LngLatLike[] = [];

    mounted() {
        this.timer = new Timer({
            timeout: mapConfig.marmenor.timer.timeout,
            immediate: true
        });

        this.timer.on("tick", async () => {
            if (this.isUpdatingMap) return;
            this.isUpdatingMap = true;

            const piezometers = await this.$api
                .getPiezometers<MeasurementPointResponse>()
                .catch(e => {
                    this.showError(`${this.$t("netError")}`);
                    console.error(e);
                })
                .finally(() => {
                    this.isUpdatingMap = false;
                });

            if (!piezometers || !piezometers.ok) return;

            this.drawPiezometers(piezometers.data);

            await sleep(500);

            if (!this.firstTime) return;
            this.firstTime = false;

            this.mapBounds = piezometers.data.map(piezometer => {
                const point = piezometer.location as Point;
                return point.coordinates as LngLatLike;
            });
        });
    }

    destroyed() {
        this.timer.stop();
    }

    async onMapLoaded(map: MBMap) {
        this.map = map;
        this.timer.start();
    }

    drawPiezometers(piezometers: MeasurementPoint[]) {
        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: piezometers.map(piezometer => {
                return {
                    type: "Feature",
                    geometry: piezometer.location,
                    properties: {
                        variableCode: piezometer.code,
                        measPoint: {
                            denomination: piezometer.denomination,
                            description: piezometer.description,
                            typology: piezometer.typology,
                            variables: piezometer.variables
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
            type: "symbol",
            layout: {
                "icon-image": PIEZOMETER_ICON_DEFAULT,
                "icon-size": 1
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
                const info = this.getFeatureDescription(
                    e.features[0].properties?.variableCode,
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
            }
        );

        this.map?.on("mouseleave", `${PIEZOMETERS_SRC}-layer`, () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            popup.remove();
        });
    }

    getFeatureDescription(variableCode: string, { denomination }) {
        return `
            <div class="map-waterbody-tooltip">
                ${denomination}
                <br/>
                (${variableCode})
            </div>
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
}
</script>

<style lang="scss" scoped>
.wrap {
    height: 90%;
    height: calc(100vh - 128px);
    width: 100%;
}
</style>
