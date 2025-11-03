import { Map as MBMap } from "mapbox-gl";

export class UDALayerControl {
    map: MBMap | null;
    container: HTMLElement;
    constructor() {
        this.map = null;
        this.container = document.createElement("div");
    }
    onAdd(map) {
        this.map = map;
        this.container = document.createElement("div");
        this.container.className = "mapboxgl-ctrl mapboxgl-ctrl-group";
        this.container.addEventListener("contextmenu", e => e.preventDefault());
        this.container.addEventListener("click", e => this.onClick());
        this.addIcon("mdi-layers");
        
        return this.container;
    }

    
    addIcon(icon){
        this.container.innerHTML =
            `<div class="tools-box">
            <button>
            <span class="mapboxgl-ctrl-icon" aria-hidden="true" title="Show UDA Layer"><i class="v-icon notranslate mdi ${icon}"></i></span>
            </button>
            </div>`;
    }

    /**
     * Show and Hide UDAs layer button
     * @param {void}
     */
    onClick(): void {
        if (
            !this.map?.getLayer("demand-units-stats") ||
            !this.map?.getLayer("demand-units-stats-outline")
        ) {
            return;
        }
        const visibility = this.map?.getLayoutProperty(
            "demand-units-stats",
            "visibility"
        );
        // Toggle layer visibility by changing the layout object's visibility property.
        if (visibility === "visible") {
            this.map?.setLayoutProperty(
                "demand-units-stats",
                "visibility",
                "none"
            );
            this.map?.setLayoutProperty(
                "demand-units-stats-outline",
                "visibility",
                "none"
            );
            this.addIcon("mdi-layers");
        } else {
            this.map?.setLayoutProperty(
                "demand-units-stats",
                "visibility",
                "visible"
            );
            this.map?.setLayoutProperty(
                "demand-units-stats-outline",
                "visibility",
                "visible"
            );
            this.addIcon("mdi-layers-off");
        }
    }
    onRemove() {
        this.container.parentNode?.removeChild(this.container);
        this.map = null;
    }
}
