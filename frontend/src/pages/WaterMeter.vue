<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox
                :center="mapCenter"
                :zoom="mapZoom"
                :mapImages="mapImages"
                @loaded="onMapLoaded"
            >
                <template v-slot:form>
                    <WaterMeterFilterForm
                        v-model="formValues"
                        @on-filter-updated="onFilterUpdated"
                    />
                </template>
            </MapBox>
            <WaterMeterDialog
                v-model="waterMeterDialog.shown"
                :point-info="waterMeterDialog.point"
                :variable-code="waterMeterDialog.variableCode"
            />
        </div>
    </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapMutations } from "vuex";
import {
    Map as MBMap,
    LngLat,
    AnySourceData,
    GeoJSONSource,
    Popup
} from "mapbox-gl";

import * as types from "@/store/types";
import { MapImageDef } from "@/components/map/MapBox.vue";
import { Timer } from "@/utils/Timer";
import { i18n } from "@/plugins/i18n";
import { mapConfig } from "@/config/map";
import {
    WaterBodyResponse,
    WaterBody,
    WaterMeterForm,
    MBMouseEvent,
    WaterMeterResponse,
    WaterMeter as WM
} from "@/interfaces";
import { FeatureCollection, Point } from "geojson";

const RIVER_ICON_DEFAULT = "river_def";
const MAP_IMAGES: MapImageDef[] = [
    {
        url: require("@/assets/img/river.png"),
        id: RIVER_ICON_DEFAULT
    }
];

type WaterBodyInfo = WaterBody & { info?: string };

const SRC_LAYERS = {
    aquifer: {
        idSrc: "aquifers",
        color: "#705CF2",
        layerConf: {
            type: "fill",
            paint: {
                "fill-color": ["get", "color"],
                "fill-opacity": 1
            }
        },
        getDescription({ name, description }) {
            return `
                <div class="map-waterbody-tooltip">
                    ${name.toLowerCase()}
                </div>
                <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
                ${description}
            `;
        }
    },
    underground: {
        idSrc: "underground",
        color: "#D9414E",
        layerConf: {
            type: "fill",
            paint: {
                "fill-color": ["get", "color"],
                "fill-opacity": 1
            }
        },
        getDescription({ name, description }) {
            return `
                <div class="map-waterbody-tooltip">
                    ${name.toLowerCase()}
                </div>
                <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
                ${description}
            `;
        }
    },
    watermeters: {
        idSrc: "watermeters",
        color: "#black",
        layerConf: {
            type: "circle",
            paint: {
                "circle-color": [
                    "case",
                    ["boolean", ["feature-state", "hover"], false],
                    "#283747",
                    "#F2DE5C"
                ],
                "circle-stroke-color": "black",
                "circle-stroke-width": 1
            }
        },
        getDescription(waterMeter: WM) {
            return `
                <div class="map-waterbody-tooltip">
                    ${waterMeter.DenominacionPunto?.toLowerCase() || ""}
                </div>
                <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
                    <div>
                        ${i18n.t(
                            "waterMeter.info.registry"
                        )}: <strong>${waterMeter.INSCRIPCION?.toLowerCase() ||
                ""}</strong>
                        </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.dossier"
                        )}: <strong>${waterMeter.OtrosExpedientes?.toLowerCase()}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.holder"
                        )}: <strong>${waterMeter.NombreTitular?.toLowerCase() ||
                ""}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.waterUse"
                        )}: <strong>${waterMeter.VolumenMaximoAnualLegal_M3?.toFixed(
                2
            ) || ""}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.code"
                        )}: <strong>${waterMeter.CodigoPVYCR.toLowerCase()}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.municipality"
                        )}: <strong>${waterMeter.MunicipioToma?.toLowerCase() ||
                ""}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.courseName"
                        )}: <strong>${waterMeter.DenominacionCauce?.toLowerCase() ||
                ""}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.status"
                        )}: <strong>${waterMeter.Funciona?.trim().toLowerCase() ||
                "?"}</strong>
                    </div>
                    <div>
                        ${i18n.t(
                            "waterMeter.info.elementID"
                        )}: <strong>${waterMeter.idElementoMedida?.toLowerCase() ||
                ""}</strong>
                        </div>
            `;
        }
    }
};

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        WaterMeterFilterForm: () =>
            import("@/pages/components/forms/WaterMeterFilterForm.vue"),
        WaterMeterDialog: () =>
            import("@/components/dialogs/WaterMeterDialog.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class WaterMeter extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.136256, 38.076218);
    mapZoom = 8;
    mapImages = Object.freeze(MAP_IMAGES);
    selectedWaterBody = false;
    selecedWaterBodyIds = new Map<string, string | number | undefined>();
    popupWaterBody = new Popup({
        closeButton: false,
        closeOnClick: false
    });

    formValues: WaterMeterForm = {
        valid: true,
        layerAqfrs: true,
        layerUndrgrnd: true,
        layerWM: true
    };

    waterMeterDialog = {
        shown: false,
        variableCode: "",
        point: {}
    };

    timer!: Timer;

    mounted() {
        // timer
        this.timer = new Timer({
            timeout: mapConfig.waterMeter.timer.timeout,
            immediate: true
        });

        this.timer.on("tick", async () => {
            this.setProgressBar(true);

            const requests = [
                this.$api.getWaterBodies<WaterBodyResponse>({
                    type: "aquifer"
                }),
                this.$api.getWaterBodies<WaterBodyResponse>({
                    type: "underground"
                }),
                this.$api.getWaterMeters<WaterMeterResponse>()
            ];

            Promise.allSettled(requests)
                .then(results => {
                    const aqRes = results[0] as PromiseSettledResult<
                        WaterBodyResponse
                    >;
                    const undRes = results[1] as PromiseSettledResult<
                        WaterBodyResponse
                    >;
                    const wmRes = results[2] as PromiseSettledResult<
                        WaterMeterResponse
                    >;

                    const failed = [
                        aqRes.status === "rejected" ? "aquifers" : null,
                        undRes.status === "rejected" ? "groundwater" : null,
                        wmRes.status === "rejected" ? "water meters" : null
                    ].filter(f => !!f);

                    if (failed.length) {
                        // this.showError(
                        //     `${this.$t("waterMeter.error")}: ${failed.join(
                        //         ", "
                        //     )}`
                        // );
                        this.showError(`${this.$t("netError")}`);
                    }

                    // UNDERGROUND WATERS
                    if (
                        undRes &&
                        undRes.status === "fulfilled" &&
                        undRes.value.ok
                    ) {
                        const data = undRes.value.data.map(wb => {
                            return {
                                ...wb,
                                info: SRC_LAYERS.underground.getDescription({
                                    name: wb.name,
                                    description: wb.type
                                })
                            };
                        });
                        this.drawWaterBodies(data, {
                            ...SRC_LAYERS.underground
                        });
                    }

                    // AQUIFERS
                    if (
                        aqRes &&
                        aqRes.status === "fulfilled" &&
                        aqRes.value.ok
                    ) {
                        const data = aqRes.value.data.map(wb => {
                            return {
                                ...wb,
                                info: SRC_LAYERS.aquifer.getDescription({
                                    name: wb.name,
                                    description: wb.type
                                })
                            };
                        });
                        this.drawWaterBodies(data, {
                            ...SRC_LAYERS.aquifer
                        });
                    }

                    // WATER METERS
                    if (
                        wmRes &&
                        wmRes.status === "fulfilled" &&
                        wmRes.value.ok
                    ) {
                        const data = wmRes.value.data.map(wm => {
                            return {
                                code: wm.CodigoPVYCR,
                                geometry: wm.location,
                                name: wm.DenominacionCauce || "",
                                type: wm.DenominacionPunto || "",
                                ["generator_flow"]: null,
                                info: SRC_LAYERS.watermeters.getDescription(wm)
                            };
                        });
                        this.drawWaterBodies(
                            data,
                            {
                                ...SRC_LAYERS.watermeters
                            },
                            (measPoint: WaterBody) => {
                                this.showWaterMeterData({
                                    variableCode: measPoint.code,
                                    point: measPoint
                                });
                            }
                        );
                    }
                })
                .finally(() => {
                    this.setProgressBar(false);
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

    /**
     * Filter event
     */
    onFilterUpdated() {
        this.setLayerVisible(
            `${SRC_LAYERS.aquifer.idSrc}-layer`,
            this.formValues.layerAqfrs
        );

        this.setLayerVisible(
            `${SRC_LAYERS.aquifer.idSrc}-layer-outline`,
            this.formValues.layerAqfrs
        );

        this.setLayerVisible(
            `${SRC_LAYERS.underground.idSrc}-layer`,
            this.formValues.layerUndrgrnd
        );

        this.setLayerVisible(
            `${SRC_LAYERS.underground.idSrc}-layer-outline`,
            this.formValues.layerUndrgrnd
        );

        this.setLayerVisible(
            `${SRC_LAYERS.watermeters.idSrc}-layer`,
            this.formValues.layerWM
        );

        this.setLayerVisible(
            `${SRC_LAYERS.watermeters.idSrc}-layer-outline`,
            this.formValues.layerWM
        );
    }

    setLayerVisible(idLayer: string, shown: boolean): void {
        const styleValue = shown ? "visible" : "none";
        this.map?.setLayoutProperty(idLayer, "visibility", styleValue);
    }

    drawWaterBodies(
        waterBodies: WaterBodyInfo[],
        { idSrc, color, layerConf },
        onClick?: (measPoint: WaterBody) => void
    ) {
        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: waterBodies.map((waterBody: WaterBodyInfo) => {
                const info = waterBody.info || "";
                return {
                    type: "Feature",
                    geometry: waterBody.geometry,
                    properties: {
                        measPoint: {
                            ...waterBody
                        },
                        color,
                        info
                    }
                };
            })
        };

        /**
         * If mapbox source exists, just update data and return
         */
        const waterBodiesSrc: AnySourceData | undefined = this.map?.getSource(
            `${idSrc}-src`
        );

        if (waterBodiesSrc) {
            (waterBodiesSrc as GeoJSONSource).setData(srcData);
            return;
        }

        /**
         * Create source and layer
         */
        this.map?.addSource(`${idSrc}-src`, {
            type: "geojson",
            data: srcData,
            generateId: true
        });

        this.map?.addLayer({
            id: `${idSrc}-layer`,
            source: `${idSrc}-src`,
            ...layerConf
        });

        this.map?.addLayer(
            {
                id: `${idSrc}-layer-outline`,
                source: `${idSrc}-src`,
                type: "line",
                layout: {},
                paint: {
                    "line-color": "#000",
                    "line-width": [
                        "case",
                        ["boolean", ["feature-state", "hover"], false],
                        4,
                        2
                    ],
                    "line-opacity": [
                        "case",
                        ["boolean", ["feature-state", "hover"], false],
                        1,
                        1
                    ]
                }
            },
            `${idSrc}-layer`
        );

        this.addMouseEvents(idSrc, onClick);
    }

    addMouseEvents(
        idSrc: string,
        onClick?: (measPoint: WaterBody) => void
    ): void {
        // Create a popup, but don't add it to the map yet.

        this.map?.on("mousemove", `${idSrc}-layer`, (e: MBMouseEvent) => {
            if (
                !this.map ||
                !e.features ||
                !e.features[0] ||
                !e.features[0].geometry ||
                this.selectedWaterBody
            )
                return;

            this.map.getCanvas().style.cursor = "pointer";

            // Description
            // const info = this.getFeatureDescriptionAquifer(
            //     JSON.parse(e.features[0].properties?.info)
            // );
            const info = e.features[0].properties?.info;

            // Populate the popup and set its coordinates
            // based on the feature found.

            if (this.selectedWaterBody && this.popupWaterBody.isOpen())
                this.popupWaterBody.remove();

            if (!this.selectedWaterBody) {
                this.popupWaterBody
                    .setLngLat(e.lngLat)
                    .setHTML(info)
                    .addTo(this.map);
            }

            /**
             * Change line width on hover
             */
            let selectedWaterBodyId = this.selecedWaterBodyIds.get(idSrc);
            if (selectedWaterBodyId !== undefined) {
                this.map.removeFeatureState({
                    source: `${idSrc}-src`,
                    id: selectedWaterBodyId
                });
            }

            selectedWaterBodyId = e.features[0].id;
            this.selecedWaterBodyIds.set(idSrc, selectedWaterBodyId);

            this.map?.setFeatureState(
                {
                    source: `${idSrc}-src`,
                    id: selectedWaterBodyId
                },
                {
                    hover: true
                }
            );
        });

        this.map?.on("mouseleave", `${idSrc}-layer`, () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            this.popupWaterBody.remove();

            const selectedWaterBodyId = this.selecedWaterBodyIds.get(idSrc);
            if (selectedWaterBodyId !== undefined) {
                this.map.setFeatureState(
                    {
                        source: `${idSrc}-src`,
                        id: selectedWaterBodyId
                    },
                    {
                        hover: false
                    }
                );
            }
            this.selecedWaterBodyIds.set(idSrc, undefined);
        });

        if (onClick) {
            this.map?.on("click", `${idSrc}-layer`, (e: MBMouseEvent) => {
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
                    coordinates[0] +=
                        e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Show dialog with info
                const props = e.features[0].properties;
                onClick({
                    ...(JSON.parse(props?.measPoint) as WaterBody)
                });
            });
        }
    }

    showWaterMeterData({ variableCode, point }): void {
        this.waterMeterDialog = {
            shown: true,
            variableCode,
            point: {
                ...point,
                name: point.name.toLowerCase(),
                type: point.type.toLowerCase()
            }
        };
    }

    showError(error: string) {
        this.setInfoMessage({ shown: true, text: error });
    }
}
</script>

<style scoped lang="scss">
.wrap {
    height: 90%;
    height: calc(100vh - 128px);
    width: 100%;
}
</style>
