<template>
    <v-container fluid pa-0 ma-0>
        <div class="wrap">
            <MapBox
                :center="mapCenter"
                :zoom="mapZoom"
                :mapImages="mapImages"
                @loaded="onMapLoaded"
            >
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
            <MeasPointDialog
                v-model="measPointDialog.shown"
                :meas-point-info="measPointDialog.point"
                :variable-code="measPointDialog.variableCode"
                :environment-flow="environmentFlow"
            />
        </div>
    </v-container>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import {
    Map as MBMap,
    LngLat,
    GeoJSONSource,
    Popup,
    LngLatLike,
    AnySourceImpl
} from "mapbox-gl";
import {
    FeatureCollection,
    Geometry,
    Point,
    MultiPoint,
    MultiLineString
} from "geojson";
import { mapMutations } from "vuex";

import { Timer } from "@/utils/Timer";
import { mapConfig } from "@/config/map";
import * as types from "@/store/types";
import {
    DroughtIndices,
    DroughtIndicesResponse,
    EnvironmentalFlow,
    EnvironmentalFlowDrought,
    EnvironmentalFlowResponse,
    LegendItem,
    MBMouseEvent,
    Variable,
    VariableResponse,
    VariableValue,
    VariableValueResponse
} from "@/interfaces";
import { MapImageDef } from "@/components/map/MapBox.vue";

interface EnvFlowPeriod {
    months: [number, number, number];
}

export const ENV_FLOW_PERIODS = new Map<string, EnvFlowPeriod>([
    ["ene_mar", { months: [0, 1, 2] }],
    ["abr_jun", { months: [3, 4, 5] }],
    ["jul_sep", { months: [6, 7, 8] }],
    ["oct_dic", { months: [9, 10, 11] }]
]);

const ENV_FLOW_SRC = "env-flows";
const MEAS_POINTS_SRC = "meas-flow";

const RIVER_ICON_DEFAULT = "river_def";
const RIVER_ICON_POSITIVE = "river_positive";
const RIVER_ICON_NEGATIVE = "river_negative";

const MAP_IMAGES: MapImageDef[] = [
    {
        url: require("@/assets/img/river.png"),
        id: RIVER_ICON_DEFAULT
    },
    {
        url: require("@/assets/img/river_negative.png"),
        id: RIVER_ICON_NEGATIVE
    },
    {
        url: require("@/assets/img/river_positive.png"),
        id: RIVER_ICON_POSITIVE
    }
];

interface EnvFlowFeature {
    color: string;
    description?: string;
    geometry: Geometry;
    lastRecordDate: string;
    limit: number;
    limitRange: string;
    name: string;
    value: number;
    variable: string;
    wbCode: string;
    inDrought: boolean;
}

export const SYSTEM_ZONES = new Map([
    [1, "UTS_I_Principal_Situacion"],
    [2, "UTS_II_Cabecera_Situacion"],
    [3, "UTS_III_RiosMI_Situacion"],
    [4, "UTS_IV_RiosMD_Situacion"]
]);

export enum DroughtStates {
    Prolonged = "Sequía prolongada",
    NotProlonged = "Ausencia de sequía prolongada"
}

@Component({
    components: {
        MapBox: () => import("@/components/map/MapBox.vue"),
        MeasPointDialog: () =>
            import("@/components/dialogs/MeasPointDialog.vue")
    },
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class EnvironmentalFlowView extends Vue {
    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    map: MBMap | null = null;
    mapCenter: LngLat = new LngLat(-1.136256, 38.076218);
    mapZoom = 8;
    environmentFlow: EnvironmentalFlowDrought[] = [];
    isUpdatingMap = false;
    timer!: Timer;
    mapImages = Object.freeze(MAP_IMAGES);

    legendItems: LegendItem[] = [
        {
            color: mapConfig.environmentFlow.colors.negative,
            text: `< ${this.$t("measPointDialog.environmentalFlow")}`
        },
        {
            color: mapConfig.environmentFlow.colors.positive,
            text: `>= ${this.$t("measPointDialog.environmentalFlow")}`
        },
        {
            color: mapConfig.environmentFlow.colors.noData,
            text: `${this.$t("chart.noData")}`
        }
    ];

    selectedEnvFlowId: string | number | undefined = undefined;
    mouseEventBlocked = false;
    measPointDialog = {
        shown: false,
        variableCode: "",
        point: {}
    };

    async mounted() {
        /**
         * Get environment flows
         */
        const envFlowRes = await this.$api
            .getEnvironmentalFlowWaterBodies<EnvironmentalFlowResponse>()
            .catch(() => {
                this.showError(`${this.$t("netError")}`);
            });

        if (!envFlowRes || !envFlowRes.ok) return;
        this.environmentFlow = envFlowRes.data;

        /**
         * Drought Indices
         */
        const latestDroughtIndices = await this.$api
            .getDroughtIndices<DroughtIndicesResponse>({
                type: "day",
                date: [new Date().toISOString()]
            })
            .catch(() => {
                this.showError(`${this.$t("netError")}`);
            });

        if (latestDroughtIndices && latestDroughtIndices.ok) {
            this.environmentFlow = this.computeDroughIndicesForFlows(
                envFlowRes.data,
                latestDroughtIndices.data
            );
        }

        /**
         * Timer
         */
        this.timer = new Timer({
            timeout: mapConfig.environmentFlow.timer.timeout,
            immediate: true
        });

        this.timer.on("tick", async () => {
            if (this.isUpdatingMap) return undefined;
            this.isUpdatingMap = true;

            this.setProgressBar(true);

            try {
                const lastDayVariableValues = await this.getLastDayVariablesValues();

                if (
                    !lastDayVariableValues ||
                    !lastDayVariableValues.ok ||
                    !lastDayVariableValues.data.length
                ) {
                    this.showError(
                        `${this.$t("environmentalFlow.noDataError")}`
                    );
                }

                const variablesInfo = await this.getVariablesInfo();

                /**
                 * Render Control points
                 */
                this.drawMeasurementPoints(
                    variablesInfo,
                    lastDayVariableValues.data,
                    this.environmentFlow
                );

                /**
                 * Render Environment flow
                 */
                const features:
                    | EnvFlowFeature[]
                    | undefined = await this.getEnvFlowFeatures(
                    lastDayVariableValues.data
                );

                this.drawEnvironmentFlow(features);
            } catch (error) {
                console.error(error);
            } finally {
                this.setProgressBar(false);
            }

            this.isUpdatingMap = false;
        });
    }

    destroyed() {
        this.timer.stop();
    }

    computeDroughIndicesForFlows(
        envFlowsData: EnvironmentalFlow[],
        droughtIndices: DroughtIndices[]
    ) {
        const droughtEnvFlows: EnvironmentalFlowDrought[] = [];
        if (droughtIndices.length === 0) return droughtEnvFlows;

        const latestDIndice = droughtIndices[0];

        for (const envFlow of envFlowsData) {
            const flowSystem = envFlow.sistema;
            const flowSM = envFlow.masa_estrategica;
            let envFlowDrought: EnvironmentalFlowDrought = {
                ...envFlow,
                inDrought: false
            };

            /**
             * Compute new range limits if "masa_estrategica" is false
             * and if the env flow belogs to a system
             * with "Sequía prolongada" state
             */

            if (!flowSM) {
                const systemZone = SYSTEM_ZONES.get(flowSystem);
                if (systemZone) {
                    if (latestDIndice[systemZone] === DroughtStates.Prolonged) {
                        // if (latestDIndice[systemZone] !== DroughtStates.Prolonged) {
                        console.log(
                            "envFlow " +
                                envFlow.variable +
                                " limits should be changed",
                            envFlow
                        );

                        envFlowDrought = this.applyProlongedLimits(envFlow);
                    }
                }
            }

            droughtEnvFlows.push(envFlowDrought);
        }

        return droughtEnvFlows;
    }

    applyProlongedLimits(envFlow: EnvironmentalFlow): EnvironmentalFlowDrought {
        return {
            ...envFlow,
            inDrought: true
        };
    }

    async onMapLoaded(map: MBMap) {
        this.map = map;

        this.timer.start();
    }

    async getLastDayVariablesValues(): Promise<VariableValueResponse> {
        /**
         * array of variables ids from environment flow ['04A03Q01', '04A04Q01', '04A02Q03'...]
         */
        const envFlowVariables = this.environmentFlow.map(
            envFlow => envFlow.variable
        );

        /**
         * Get last values foreach env flow variable
         */
        const endDate = new Date(
            mapConfig.environmentFlow.dateReference || new Date()
        );

        const startDate = new Date(endDate);
        startDate.setDate(startDate.getDate() - 1);

        return await this.$api.getVariablesValues<VariableValueResponse>(
            envFlowVariables,
            startDate,
            endDate,
            "mean",
            "1d"
        );
    }

    /**
     * Get variable geometry and color depending on its
     * last flow value
     */
    async getEnvFlowFeatures(
        lastDayVariableValues: VariableValue[]
    ): Promise<EnvFlowFeature[] | undefined> {
        /**
         * Date range: ene_mar, abr_jun, jul_sep, oct_dec
         */
        const dateRange = this.getCurrentDateRange();

        /**
         * Filter env variables. We only want the existing ones
         */
        const filteredVariables = this.environmentFlow.filter(variable => {
            return lastDayVariableValues.some(
                lastValVar => lastValVar.variableCode === variable.variable
            );
        });

        /**
         * mapbox features foreach variable
         */
        const features: EnvFlowFeature[] = filteredVariables.map(variable => {
            const envColors = mapConfig.environmentFlow.colors;
            let color = envColors.noData;

            // getting lastest values of variable
            const lastValuesOfVar = lastDayVariableValues.filter(
                lastValVar => lastValVar.variableCode === variable.variable
            );

            /**
             * a variable could have more than one record
             * so get the last of them
             */
            const lastValueOfVar =
                lastValuesOfVar[lastValuesOfVar.length - 1] || null;

            const range = dateRange + (variable.inDrought ? "_seq" : "");

            if (lastValueOfVar) {
                const curValue = lastValueOfVar._value;

                color =
                    curValue < variable[range]
                        ? envColors.negative
                        : envColors.positive;
            }

            return {
                variable: variable.variable,
                color: color,
                geometry: variable.water_body.geometry,
                name: variable.water_body.name,
                wbCode: variable.water_body.code,
                value: lastValueOfVar._value,
                limit: variable[range],
                limitRange: dateRange,
                inDrought: variable.inDrought || false,
                lastRecordDate: new Date(
                    lastValueOfVar._time
                ).toLocaleDateString()
            };
        });

        return features;
    }

    /**
     * Search for the correct range for today
     */
    getCurrentDateRange(): string {
        let range = ENV_FLOW_PERIODS.keys().next().value;
        const today = new Date(
            mapConfig.environmentFlow.dateReference || new Date()
        );

        ENV_FLOW_PERIODS.forEach((config: EnvFlowPeriod, key: string) => {
            const { months } = config;

            if (months.indexOf(today.getMonth()) !== -1) {
                range = key;
            }
        });

        return range;
    }

    /**
     * Env flow Popup <html> window info.
     */
    getFeatureDescription(body: Partial<EnvFlowFeature>): string {
        const description = body.description
            ? `
                <div style="text-align: left;">
                    ${body.description}
                </div>
            `
            : "";

        return `
            <div class="map-waterbody-tooltip">
                ${body.name} <br/>
                (${body.wbCode})
            </div>
            ${description}
            <hr style="border: none; border-top: 1px dashed #bfbfbf; color: #bfbfbf; margin: 0.5rem 0;">
            <div>
                <div>
                    ${this.$t("environmentalFlow.popupMean")}: <strong>
                        ${body.value?.toFixed(4) || "?"}
                        (m<sup>3</sup>/s)</strong>
                </div>
                <div>
                    ${this.$t("environmentalFlow.limitRange")}:
                    <strong>${body.limit} (m<sup>3</sup>/s)</strong>
                    (${this.$t("environmentalFlow." + body.limitRange)})
                </div>
                <div>
                    ${this.$t("droughtIndices.prolongedDrought")}:
                    <strong>${
                        body.inDrought
                            ? `<span style='color:red'>${this.$t("yes")}</span>`
                            : `${this.$t("no")}`
                    }</strong>
                </div>

            </div>
        `;
    }

    /**
     * Draw environment flows on mapbox using line layer
     */
    drawEnvironmentFlow(features: EnvFlowFeature[] | undefined): void {
        if (!features || !features.length) return;

        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: features.map(body => {
                return {
                    type: "Feature",
                    geometry: body.geometry,
                    properties: {
                        color: body.color,
                        description: this.getFeatureDescription(body)
                    }
                };
            })
        };

        /**
         * If mapbox source exists, just update data and return
         */
        const envFlowSrc: AnySourceImpl | undefined = this.map?.getSource(
            `${ENV_FLOW_SRC}-src`
        );

        if (envFlowSrc) {
            (envFlowSrc as GeoJSONSource).setData(srcData);
            return;
        }

        /**
         * Create source and layer
         */
        this.map?.addSource(`${ENV_FLOW_SRC}-src`, {
            type: "geojson",
            data: srcData,
            generateId: true
        });

        this.map?.addLayer(
            {
                id: `${ENV_FLOW_SRC}-layer`,
                source: `${ENV_FLOW_SRC}-src`,
                type: "line",
                paint: {
                    "line-width": [
                        "case",
                        ["==", ["feature-state", "hover"], true],
                        5,
                        ["==", ["feature-state", "hover"], false],
                        3,
                        3
                    ],
                    "line-color": ["get", "color"]
                }
            },
            `${MEAS_POINTS_SRC}-layer`
        );

        this.addEnvFlowMouseEvents();
    }

    /**
     * Add mouseenter and mouseleave to modify line width on hover
     */
    addEnvFlowMouseEvents(): void {
        // Create a popup, but don't add it to the map yet.
        const popup = new Popup({
            closeButton: false,
            closeOnClick: false
        });

        this.map?.on(
            "mouseenter",
            `${ENV_FLOW_SRC}-layer`,
            (e: MBMouseEvent) => {
                if (
                    !this.map ||
                    this.mouseEventBlocked ||
                    !e.features ||
                    !e.features[0] ||
                    !e.features[0].geometry
                )
                    return;

                this.map.getCanvas().style.cursor = "pointer";

                let coordinates = (e.features[0].geometry as MultiPoint)
                    .coordinates;

                if (e.features[0].geometry.type === "MultiLineString") {
                    const multiCoordinates = (e.features[0]
                        .geometry as MultiLineString).coordinates;
                    coordinates = multiCoordinates[0].slice();
                }

                // Get the midpoint of all coordinates
                const midPointCoords = coordinates[
                    Math.round(coordinates.length * 0.5)
                ].slice();

                // Description
                const description = e.features[0].properties?.description || "";

                // Ensure that if the map is zoomed out such that multiple
                // copies of the feature are visible, the popup appears
                // over the copy being pointed to.
                while (Math.abs(e.lngLat.lng - midPointCoords[0]) > 180) {
                    midPointCoords[0] +=
                        e.lngLat.lng > midPointCoords[0] ? 360 : -360;
                }

                // Populate the popup and set its coordinates
                // based on the feature found.
                popup
                    .setLngLat(midPointCoords as LngLatLike)
                    .setHTML(description)
                    .addTo(this.map);

                /**
                 * Change line width on hover
                 */
                if (this.selectedEnvFlowId !== undefined) {
                    this.map.removeFeatureState({
                        source: `${ENV_FLOW_SRC}-src`,
                        id: this.selectedEnvFlowId
                    });
                }

                this.selectedEnvFlowId = e.features[0].id;

                this.map?.setFeatureState(
                    {
                        source: `${ENV_FLOW_SRC}-src`,
                        id: this.selectedEnvFlowId
                    },
                    {
                        hover: true
                    }
                );
            }
        );

        this.map?.on("mouseleave", `${ENV_FLOW_SRC}-layer`, () => {
            if (!this.map) return;

            this.map.getCanvas().style.cursor = "";

            popup.remove();

            if (this.selectedEnvFlowId !== undefined) {
                this.map.setFeatureState(
                    {
                        source: `${ENV_FLOW_SRC}-src`,
                        id: this.selectedEnvFlowId
                    },
                    {
                        hover: false
                    }
                );
            }
            this.selectedEnvFlowId = undefined;
        });
    }

    /**
     * Get measurement points features to be drawn
     */
    async getVariablesInfo(): Promise<Variable[] | undefined> {
        /**
         * array of variables ids from environment flow ['04A03Q01', '04A04Q01', '04A02Q03'...]
         */
        const envFlowVariables = this.environmentFlow.map(
            envFlow => envFlow.variable
        );

        this.setProgressBar(true);

        /**
         * Get last values foreach env flow variable
         */
        const variablesInfo = await this.$api
            .getVariables<VariableResponse>(envFlowVariables)
            .catch(e => console.log(e))
            .finally(() => this.setProgressBar(false));

        if (!variablesInfo || !variablesInfo.ok) return;

        return variablesInfo.data;
    }

    /**
     * Draw measurement points on mapbox using icons layer
     */
    drawMeasurementPoints(
        variablesInfo: Variable[] | undefined,
        lastDayVariableValues: VariableValue[],
        envFlowVariables: EnvironmentalFlowDrought[]
    ): void {
        if (!variablesInfo || !variablesInfo.length) return;

        /**
         * Date range: ene_mar, abr_jun, jul_sep, oct_dec
         */
        const dateRange = this.getCurrentDateRange();

        /**
         * Filter env variables. We only want the existing ones
         */
        const filteredVariables = variablesInfo.filter(variable => {
            return lastDayVariableValues.some(
                lastValVar => lastValVar.variableCode === variable.code
            );
        });

        const srcData: FeatureCollection = {
            type: "FeatureCollection",
            features: filteredVariables.map(variableInfo => {
                // getting lastest values of variable
                const lastValuesOfVar = lastDayVariableValues.filter(
                    lastValVar => lastValVar.variableCode === variableInfo.code
                );

                /**
                 * a variable could have more than one record
                 * so get the last of them
                 */
                const lastValueOfVar =
                    lastValuesOfVar[lastValuesOfVar.length - 1] || null;

                let icon = RIVER_ICON_DEFAULT;

                const envFlowVariable = envFlowVariables.find(
                    envFlowVar => envFlowVar.variable === variableInfo.code
                );

                const range =
                    dateRange + (envFlowVariable?.inDrought ? "_seq" : "");

                let curValue: undefined | number = undefined;
                if (lastValueOfVar && envFlowVariable) {
                    curValue = lastValueOfVar._value;
                    icon =
                        curValue < envFlowVariable[range]
                            ? RIVER_ICON_NEGATIVE
                            : RIVER_ICON_POSITIVE;
                }

                const point = variableInfo.measurement_point;

                return {
                    type: "Feature",
                    geometry: point.location,
                    properties: {
                        icon: icon,
                        variableCode: variableInfo.code,
                        info: this.getFeatureDescription({
                            name: point.denomination,
                            description: point.description,
                            wbCode: variableInfo.code,
                            value: curValue || 0,
                            limit: envFlowVariable
                                ? envFlowVariable[range]
                                : "?",
                            limitRange: dateRange,
                            inDrought: envFlowVariable?.inDrought || false,
                            lastRecordDate: new Date(
                                lastValueOfVar._time
                            ).toLocaleDateString()
                        }),
                        measPoint: {
                            denomination: point.denomination,
                            description: point.description,
                            typology: point.typology
                        }
                    }
                };
            })
        };

        /**
         * If mapbox source exists, just update data and return
         */
        const measPontsSrc: AnySourceImpl | undefined = this.map?.getSource(
            `${MEAS_POINTS_SRC}-src`
        );

        if (measPontsSrc) {
            (measPontsSrc as GeoJSONSource).setData(srcData);
            return;
        }

        /**
         * Create source and layer
         */
        this.map?.addSource(`${MEAS_POINTS_SRC}-src`, {
            type: "geojson",
            data: srcData
        });

        this.map?.addLayer({
            id: `${MEAS_POINTS_SRC}-layer`,
            source: `${MEAS_POINTS_SRC}-src`,
            type: "symbol",
            layout: {
                "icon-image": ["get", "icon"],
                "icon-size": 1
            }
        });

        this.addMeasPointsMouseEvents();
    }

    /**
     * Add click event to show the measurement point info
     */
    addMeasPointsMouseEvents(): void {
        // Create a popup, but don't add it to the map yet.
        const popup = new Popup({
            closeButton: false,
            closeOnClick: false
        });

        this.map?.on("click", `${MEAS_POINTS_SRC}-layer`, (e: MBMouseEvent) => {
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
            this.showMeasurementPointData({
                variableCode: props?.variableCode,
                point: JSON.parse(props?.measPoint)
            });
        });

        // Change the cursor to a pointer when the mouse is over the places layer.
        this.map?.on(
            "mouseenter",
            `${MEAS_POINTS_SRC}-layer`,
            (e: MBMouseEvent) => {
                if (
                    !this.map ||
                    !e.features ||
                    !e.features[0] ||
                    !e.features[0].geometry
                )
                    return;

                this.mouseEventBlocked = true;

                // Copy coordinates array.
                const coordinates = (e.features[0].geometry as Point)
                    .coordinates;

                // Description
                const info = e.features[0].properties?.info || "";

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

                this.map.getCanvas().style.cursor = "pointer";
            }
        );

        // Change it back to a pointer when it leaves.
        this.map?.on("mouseleave", `${MEAS_POINTS_SRC}-layer`, () => {
            if (!this.map) return;

            this.mouseEventBlocked = false;

            popup.remove();

            this.map.getCanvas().style.cursor = "";
        });
    }

    /**
     * Show measurement point data plot
     */
    showMeasurementPointData({ variableCode, point }): void {
        this.measPointDialog = {
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
