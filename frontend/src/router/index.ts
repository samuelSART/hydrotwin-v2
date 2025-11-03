import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import store from "@/store";
import * as types from "@/store/types";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
    {
        path: "/",
        component: () => import("@/pages/index.vue"),
        children: [
            {
                name: "documentation",
                path: "documentation",
                component: () => import("@/pages/Documentation.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "environmentalFlow",
                path: "",
                component: () => import("@/pages/EnvironmentalFlow.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "dams",
                path: "/dams",
                component: () => import("@/pages/Dams.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "piezometry",
                path: "/piezometry",
                component: () => import("@/pages/piezometry/CPPiezometers.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "marmenor",
                path: "/marmenor",
                component: () => import("@/pages/piezometry/Piezometers.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "qualitySaica",
                path: "/qualitySaica",
                component: () => import("@/pages/QualitySaica.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "waterMeter",
                path: "/watermeter",
                component: () => import("@/pages/WaterMeter.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "meteo",
                path: "/meteo",
                component: () => import("@/pages/Aemet.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "droughtIndices",
                path: "/droughtindices",
                component: () => import("@/pages/DroughtIndices.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "l1",
                path: "/l1",
                component: () => import("@/pages/Predictions.vue"),
                meta: {
                    authentication: true
                },
                props: { line: 1 }
            },
            {
                name: "l2",
                path: "/l2",
                component: () => import("@/pages/Predictions.vue"),
                props: { line: 2 },
                meta: {
                    authentication: true
                }
            },
            {
                name: "l3",
                path: "/l3",
                component: () => import("@/pages/Predictions.vue"),
                props: { line: 3 },
                meta: {
                    authentication: true
                }
            },
            {
                name: "l4",
                path: "/l4/dashboard/:type?/:ud?",
                component: () => import("@/pages/Planner.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "hydroScheme",
                path: "l4/hydroScheme",
                component: () => import("@/pages/HydroScheme.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "co2",
                path: "l4/co2",
                component: () => import("@/pages/CO2.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "hydroEconomic",
                path: "l4/hydroEconomic",
                component: () => import("@/pages/HydroEconomic.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "l5",
                path: "/l5/dashboard/:type?/:ud?",
                component: () => import("@/pages/Optimizer.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "hydroScheme",
                path: "l5/hydroScheme",
                component: () => import("@/pages/HydroScheme.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "co2",
                path: "l5/co2",
                component: () => import("@/pages/CO2.vue"),
                meta: {
                    authentication: true
                }
            },
            {
                name: "hydroEconomic",
                path: "l5/hydroEconomic",
                component: () => import("@/pages/HydroEconomic.vue"),
                meta: {
                    authentication: true
                }
            }
        ]
    },
    {
        path: "/signin",
        name: "Signin",
        component: () => import("@/pages/auth/SigninForm.vue")
    }
];

const router = new VueRouter({
    routes
});

router.beforeEach((to, from, next) => {
    if (process.env.VUE_APP_NO_CAS_AUTH) {
        next();
        return;
    }

    const authRequired = to.matched.some(record => record.meta.authentication);
    const loggedIn = Boolean(store.getters[types.AUTH_USERNAME]);

    // Trying to access a restricted page + not logged in
    // redirect to login page
    if (authRequired && !loggedIn) {
        next("/signin");
    } else {
        next();
    }
});

export default router;
