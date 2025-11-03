<template>
    <div class="layout-fab">
        <v-navigation-drawer
            right
            v-model="syncFilterFormPanelShow"
            temporary
            fixed
            disable-resize-watcher
            width="315"
            hide-overlay
        >
            <v-app-bar color="primary" dark dense>
                <v-toolbar-title>
                    Filter
                </v-toolbar-title>
                <v-tooltip left>
                    <template v-slot:activator="{ on }">
                        <v-btn
                            absolute
                            dark
                            fab
                            bottom
                            right
                            small
                            color="error"
                            v-on="on"
                            :loading="filterLoading"
                            :class="{ 'v-btn-disabled': filterLoading }"
                            @click.stop="setFilter"
                        >
                            <v-icon>mdi-refresh</v-icon>
                        </v-btn>
                    </template>
                    <span>Refresh</span>
                </v-tooltip>
            </v-app-bar>
            <v-divider />
            <v-container :class="{ 'v-container-overlay': filterLoading }">
                <slot name="form"></slot>
            </v-container>
        </v-navigation-drawer>
    </div>
</template>

<script lang="ts">
import { Vue, Component, PropSync } from "vue-property-decorator";
import { mapGetters } from "vuex";

import * as types from "@/store/types";

@Component({
    computed: {
        ...mapGetters({
            filterLoading: types.APP_FILTER_LOADING
        })
    }
})
export default class FilterFormPanelBase extends Vue {
    @PropSync("filterFormPanelShow", { type: Boolean || null })
    syncFilterFormPanelShow!: null;

    /**
     * Methods
     */
    onFilterPanelInput(state) {
        this.syncFilterFormPanelShow = state;
    }

    setFilter() {
        this.$emit("on-filter-updated");
    }
}
</script>

<style>
.v-btn-disabled {
    cursor: default;
    pointer-events: none;
}
.v-container-overlay {
    height: 100%;
    pointer-events: none;
    background-color: rgba(83, 77, 77, 0.46);
    pointer-events: none;
}
.v-navigation-drawer__content {
    overflow-y: hidden !important;
}
</style>
