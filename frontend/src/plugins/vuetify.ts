import Vue from "vue";
import Vuetify from "vuetify/lib";

const lightTheme = {
    primary: "#283747",
    secondary: "#85C1E9"
};

Vue.use(Vuetify);

export default new Vuetify({
    theme: {
        options: {
            customProperties: true
        },
        themes: {
            light: lightTheme
        }
    }
});
