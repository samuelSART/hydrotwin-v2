import Vue from "vue";

import App from "./App.vue";
import router from "./router";
import store from "./store";
import { i18n } from "./plugins/i18n";
import vuetify from "./plugins/vuetify";
import { APIServicePlugin } from "./plugins/api-service/api.service";
import VueCookies from "vue-cookies";
import { worker } from "./mocks/browser.js";
import * as echarts from "echarts";

// Echarts theme
import echartsTheme from "@/assets/charts/hydrotwin.json";
import echartsDashboardTheme from "@/assets/charts/hydrotwinDashboard.json";
echarts.registerTheme("hydrotwin", echartsTheme);
echarts.registerTheme("hydrotwin_dashboard", echartsDashboardTheme);
// NEW
if (process.env.NODE_ENV === "development") {
    worker.start();
}

// Vue config
Vue.config.productionTip = false;
Vue.use(APIServicePlugin);
Vue.use(VueCookies);

new Vue({
    router,
    store,
    i18n,
    vuetify,
    render: h => h(App)
}).$mount("#app");
