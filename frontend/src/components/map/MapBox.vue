<template>
    <div class="full-screen">
        <div id="map" class="full-screen"></div>
        <div v-if="$slots.form" class="map-form-overlay">
            <slot name="form"></slot>
        </div>
        <div v-if="$slots.info" class="map-info-overlay">
            <slot name="info"></slot>
        </div>
        <div v-if="$slots.plot" class="map-plot-overlay">
            <slot name="plot"></slot>
        </div>
        <div v-if="$slots.legend" class="map-legend-overlay">
            <slot name="legend"></slot>
        </div>
    </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Watch, PropSync } from "vue-property-decorator";
import { mapMutations } from "vuex";
import mapboxgl, {
    Map as MBMap,
    LngLat,
    LngLatBounds,
    LngLatLike
} from "mapbox-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "mapbox-gl/dist/mapbox-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import MapboxGeocoder from "@mapbox/mapbox-gl-geocoder";
import "@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css";
import { mapConfig } from "@/config/map";
import * as types from "@/store/types";

export type MapImageDef = {
    id: string;
    url: string;
};

const BACKGROUND = {
    NAME: "basin-background"
};

@Component({
    methods: {
        ...mapMutations({
            setProgressBar: types.MUTATE_APP_PROGRESSBAR,
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    }
})
export default class MapBox extends Vue {
    @Prop({ type: LngLat, required: true }) center!: LngLat;
    @Prop({ type: Number, required: true }) zoom!: number;
    @PropSync("drawer", { type: Boolean })
    drawerAvailable!: boolean;
    @Prop({ type: Boolean, required: false, default: true })
    showBoundaries!: boolean;
    @Prop({ type: Boolean, required: false, default: true })
    showWaterBodies!: boolean;
    @Prop({ type: Array, required: false, default: () => [] })
    mapImages!: Array<MapImageDef>;
    @Prop({ type: Array, required: false, default: () => [] })
    mapBounds!: Array<LngLatLike>;

    setProgressBar!: (state: boolean) => void;
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;

    map: MBMap | null = null;
    legend = document.getElementById("legend");
    plot = document.getElementById("plot");
    mapdraw: MapboxDraw = new MapboxDraw({
        displayControlsDefault: false,
        controls: {
            polygon: true,
            point: true,
            trash: true
        }
    });

    @Watch("mapBounds")
    onMapBoundsChanged() {
        if (!this.mapBounds.length) return;
        this.fitMapBounds(this.mapBounds);
    }

    @Watch("drawerAvailable")
    onDrawerAvailableChanged() {
        if (this.map) {
            if (this.drawerAvailable) {
                this.map?.addControl(this.mapdraw, "top-left");
            } else {
                this.map?.removeControl(this.mapdraw);
            }
        }
    }

    mounted() {
        mapboxgl.accessToken = mapConfig.accessToken;
        this.map = this.initMap();

        this.map.on("load", async () => {
            await this.loadMapImages();

            this.$emit("loaded", this.map);

            (this.showBoundaries || this.showWaterBodies) &&
                this.drawMapBackgroundLayers();
        });
    }

    removeAllDraws() {
        if (this.mapdraw) {
            this.mapdraw.deleteAll();
        }
    }

    loadMapImages() {
        return Promise.all(
            this.mapImages.map(
                img =>
                    new Promise(resolve => {
                        this.map?.loadImage(img.url, (error, res) => {
                            if (error || !res) return;

                            this.map?.addImage(img.id, res);

                            resolve(true);
                        });
                    })
            )
        );
    }

    initMap(): MBMap {
        const map = new mapboxgl.Map({
            container: "map",
            style: mapConfig.style,
            center: this.center,
            zoom: this.zoom
        });

        map.addControl(
            new MapboxGeocoder({
                accessToken: mapboxgl.accessToken,
                mapboxgl: mapboxgl
            }),
            "top-left"
        );

        if (this.drawerAvailable) {
            map.addControl(this.mapdraw, "top-left");
        }
        map.on("draw.create", this.onCreatePolygon);
        map.on("draw.delete", this.onDeletePolygon);
        map.on("draw.update", this.onUpdatePolygon);

        return map;
    }

    drawMapBackgroundLayers(): void {
        this.map?.addSource(BACKGROUND.NAME, {
            type: "raster",
            tiles: [this.backgroundTile],
            tileSize: 256
        });

        this.map?.addLayer({
            id: BACKGROUND.NAME,
            type: "raster",
            source: BACKGROUND.NAME,
            paint: {
                "raster-opacity": 0.6
            }
        });
    }

    fitMapBounds(coordinates: LngLatLike[], padding = 100) {
        const bounds = new LngLatBounds(coordinates[0], coordinates[0]);

        // Extend the 'LngLatBounds' to include every coordinate in the bounds result.
        for (const coord of coordinates) {
            bounds.extend(coord);
        }

        this.map?.fitBounds(bounds, {
            padding
        });
    }

    onCreatePolygon(e): void {
        this.$emit("createPolygon", e);
    }

    onDeletePolygon(e): void {
        this.$emit("deletePolygon", e);
    }

    onUpdatePolygon(e): void {
        this.$emit("updatePolygon", e);
    }

    get backgroundTile() {
        const boundaries = this.showBoundaries ? [131] : [];
        const waterBodies = this.showWaterBodies ? [53, 77, 80] : [];
        const units = boundaries.concat(waterBodies).join(",");

        return `https://www.chsegura.es/server/rest/services/VISOR_CHSIC3/VISOR_PUBLICO_ETRS89_v5_vectorial_dinamico/MapServer/export?dpi=96&transparent=true&format=png32&layers=show:${units}&bbox={bbox-epsg-3857}&bboxSR=3857&imageSR=3857&size=256,256&f=image`;
    }
}
</script>

<style lang="scss">
.full-screen {
    height: 100%;
    width: 100%;
}

.map-legend-overlay {
    position: absolute;
    bottom: 95px;
    right: 1%;
    background: #fff;
    overflow: auto;
    border-radius: 5px;
}

.map-plot-overlay {
    position: absolute;
    width: 50%;
    height: auto;
    bottom: 10%;
    left: 1%;
    padding: 0px;
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
.map-info-overlay {
    position: absolute;
    bottom: 12%;
    left: 1%;
    background: #fff;
    overflow: auto;
    border-radius: 5px;
}

.map-form-overlay {
    position: absolute;
    width: 18%;
    top: 1%;
    right: 1%;
    padding: 10px;
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
</style>

<style>
.map-waterbody-tooltip {
    text-align: left;
    font-weight: bold;
}

.mapboxgl-popup {
    pointer-events: none !important;
}

.mapboxgl-popup-content {
    pointer-events: none !important;
}
</style>
