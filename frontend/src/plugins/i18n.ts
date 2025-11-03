import Vue from "vue";
import VueI18n from "vue-i18n";
import en from "../locales/en.json";
import es from "../locales/es.json";

Vue.use(VueI18n);

export const i18n = new VueI18n({
    locale:
        process.env.VUE_APP_I18N_LOCALE || navigator.language.substring(0, 2),
    fallbackLocale: process.env.VUE_APP_I18N_FALLBACK_LOCALE || "es",
    messages: { es, en }
});

if (module.hot) {
    module.hot.accept(["../locales/en.json", "../locales/es.json"], () => {
        i18n.setLocaleMessage("en", require("../locales/en.json").default);
        i18n.setLocaleMessage("es", require("../locales/es.json").default);
    });
}
