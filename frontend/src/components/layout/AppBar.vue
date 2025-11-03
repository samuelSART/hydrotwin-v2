<template>
    <v-app-bar app flat height="64px" class="app-bar-underline">
        <v-app-bar-nav-icon
            @click.stop="setDrawer(!drawer)"
        ></v-app-bar-nav-icon>

        <v-toolbar-title class="mr-4 pl-0 align-center">
            <span class="title primary--text">
                {{ $t(`appBar.${getRouteName()}`) }}
            </span>
            <v-btn
                icon
                x-small
                color="primary"
                class="ml-1"
                @click="onHelpBtnClick"
                v-if="existHelperText"
            >
                <v-icon>mdi-help-rhombus-outline</v-icon>
            </v-btn>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <div class="d-flex">
            <v-img
                alt="HydroTwin Logo"
                class="shrink mr-2 ml-0"
                contain
                src="@/assets/img/logo_ht_chs.png"
                transition="scale-transition"
                width="110"
            />
            <v-img
                alt="CHS"
                class="shrink mr-2 ml-0"
                contain
                src="@/assets/img/CHS.jpeg"
                transition="scale-transition"
                width="50"
            />
        </div>

        <HelpDialog v-model="dialog" :html-content="helperComponentHTML" />
    </v-app-bar>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapGetters, mapMutations } from "vuex";

import * as types from "@/store/types";

@Component({
    components: {
        HelpDialog: () => import("@/components/dialogs/HelpDialog.vue")
    },
    computed: {
        ...mapGetters({
            drawer: types.APP_DRAWER
        })
    },
    methods: {
        ...mapMutations({
            setDrawer: types.MUTATE_APP_DRAWER
        })
    }
})
export default class AppBar extends Vue {
    setDrawer!: (state: boolean) => void;
    drawer!: boolean;

    dialog = false;
    helperComponentHTML = "";

    /**
     * Methods
     */
    getRouteName() {
        return this.$route.name;
    }

    onHelpBtnClick() {
        this.dialog = true;
        this.helperComponentHTML = this.$t(
            "help." + this.$route.name
        ).toString();
    }

    /**
     * Find if current view has its help translation text
     */
    get existHelperText() {
        const currentView = this.$route.name;
        const transKey = "help." + currentView;

        return this.$i18n.te(transKey);
    }
}
</script>

<style lang="scss" scoped>
.app-bar-underline {
    border-bottom: 1px solid #dadce0;
    background-color: white !important;
}
</style>
