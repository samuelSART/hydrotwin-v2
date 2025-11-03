<template>
    <v-navigation-drawer
        id="core-navigation-drawer"
        :mini-variant.sync="drawer"
        :expand-on-hover="false"
        mobile-breakpoint="960"
        app
        permanent
        width="350"
        color="primary"
        dark
    >
        <v-list dense nav class="pa-1 pb-1 pt-1">
            <v-list-group :value="false" active-class="secondary">
                <!-- Activator -->
                <template v-slot:activator>
                    <v-list-item-avatar
                        color="secondary"
                        min-height="35"
                        min-width="35"
                        width="35"
                        height="35"
                    >
                        <v-img src="@/assets/img/profile_pic.png" />
                    </v-list-item-avatar>

                    <v-list-item-content>
                        <v-list-item-title class="text-md-body-1">
                            {{ userName || "" }}
                        </v-list-item-title>
                    </v-list-item-content>
                </template>

                <v-list-item link class="pl-4" @click.stop="logout">
                    <v-list-item-action>
                        <v-icon>mdi-logout</v-icon>
                    </v-list-item-action>
                    <v-list-item-title>
                        {{ $t("drawer.signOut") }}
                    </v-list-item-title>
                </v-list-item>
            </v-list-group>
        </v-list>

        <v-divider class="ml-5 mr-5" />
        <v-list expand nav dense>
            <v-list-item-group>
                <v-list-item
                    v-for="item in sections"
                    :key="item.title"
                    :to="item.to"
                    active-class="active"
                    :alt="$t(`drawer.${item.title}`)"
                    :title="$t(`drawer.${item.title}`)"
                >
                    <v-list-item-action>
                        <v-icon>{{ item.icon }}</v-icon>
                    </v-list-item-action>

                    <v-list-item-content>
                        <v-list-item-title>
                            {{ $t(`drawer.${item.title}`) }}
                        </v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list-item-group>
            <v-list-group
                :value="false"
                active-class="secondary"
                v-for="item in sectionsWithChildrens"
                :key="item.title"
            >
                <template v-slot:activator>
                    <v-list-item-action>
                        <v-icon>{{ item.icon }}</v-icon>
                    </v-list-item-action>

                    <v-list-item-content>
                        <v-list-item-title>
                            {{ $t(`drawer.${item.title}`) }}
                        </v-list-item-title>
                    </v-list-item-content>
                </template>

                <v-list-item
                    v-for="children in item.childrens"
                    :key="children.title"
                    :to="children.to"
                    active-class="active"
                    class="pl-4"
                >
                    <v-list-item-action>
                        <v-icon>{{ children.icon }}</v-icon>
                    </v-list-item-action>
                    <v-list-item-title>
                        {{ $t(`drawer.${children.title}`) }}
                    </v-list-item-title>
                </v-list-item>
            </v-list-group>
        </v-list>
        <!-- <template v-slot:append>
            <div class="version pa-2">version: {{ version }}</div>
        </template> -->
    </v-navigation-drawer>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapMutations, mapActions, mapGetters } from "vuex";

import * as types from "@/store/types";

@Component({
    computed: {
        ...mapGetters({
            userName: types.AUTH_USERNAME
        })
    },
    methods: {
        ...mapMutations({
            setDrawer: types.MUTATE_APP_DRAWER
        }),
        ...mapActions({
            authLogout: types.AUTH_LOGOUT
        })
    }
})
export default class Drawer extends Vue {
    setDrawer!: (state: boolean) => void;
    authLogout!: () => void;
    userName!: string;

    version = process.env.VUE_APP_VERSION || "nover";

    items = [
        {
            title: "documentation",
            icon: "mdi-text-box-multiple-outline",
            to: "/documentation"
        },
        {
            title: "environmentalFlow",
            icon: "mdi-waves",
            to: "/"
        },
        {
            title: "dams",
            icon: "mdi-waterfall",
            to: "/dams"
        },
        {
            title: "piezometry",
            icon: "mdi-sign-pole",
            to: "/piezometry"
        },
        {
            title: "marmenor",
            icon: "mdi-sign-pole",
            to: "/marmenor"
        },
        {
            title: "qualitySaica",
            icon: "mdi-check-outline",
            to: "/qualitysaica"
        },
        {
            title: "waterMeter",
            icon: "mdi-water-circle",
            to: "/watermeter"
        },
        {
            title: "meteo",
            icon: "mdi-weather-cloudy",
            to: "/meteo"
        },
        {
            title: "droughtIndices",
            icon: "mdi-water-alert",
            to: "/droughtindices"
        },
        {
            title: "l1",
            icon: "mdi-weather-partly-snowy-rainy",
            to: "/l1"
        },
        {
            title: "l2",
            icon: "mdi-weather-cloudy-arrow-right",
            to: "/l2"
        },
        {
            title: "l3",
            icon: "mdi-spa",
            to: "/l3"
        }
    ];

    itemsWithChildrens = [
        {
            title: "l4",
            icon: "mdi-calendar-range",
            to: "/l4",
            childrens: [
                {
                    title: "dashboard",
                    icon: "mdi-monitor-dashboard",
                    to: "/l4/dashboard"
                },
                {
                    title: "hydroScheme",
                    icon: "mdi-map",
                    to: "/l4/hydroscheme"
                },
                {
                    title: "co2",
                    icon: "mdi-molecule-co2",
                    to: "/l4/co2"
                },
                {
                    title: "hydroEconomic",
                    icon: "mdi-finance",
                    to: "/l4/hydroeconomic"
                }
            ]
        },
        {
            title: "l5",
            icon: "mdi-wrench-clock",
            to: "/l5",
            childrens: [
                {
                    title: "dashboard",
                    icon: "mdi-monitor-dashboard",
                    to: "/l5/dashboard"
                },
                {
                    title: "hydroScheme",
                    icon: "mdi-map",
                    to: "/l5/hydroscheme"
                },
                {
                    title: "co2",
                    icon: "mdi-molecule-co2",
                    to: "/l5/co2"
                },
                {
                    title: "hydroEconomic",
                    icon: "mdi-finance",
                    to: "/l5/hydroeconomic"
                }
            ]
        }
    ];

    /**
     * Computed
     */

    get drawer() {
        return this.$store.state.app.drawer;
    }

    set drawer(val) {
        this.setDrawer(val);
    }

    get sections() {
        return this.items;
    }

    get sectionsWithChildrens() {
        return this.itemsWithChildrens;
    }

    /**
     * Methods
     */
    logout() {
        this.authLogout();
    }
}
</script>

<style lang="scss" scoped>
.active {
    background-color: var(--v-secondary-base);
}
.version {
    color: white;
    font-weight: bold;
    font-size: small;
}
</style>
