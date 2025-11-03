module.exports = {
    transpileDependencies: ["vuetify"],
    pages: {
        index: {
            title: "Gemelo Digital - CHS",
            template: "public/index.html",
            entry: "src/main.ts"
        }
    },
    pluginOptions: {
        i18n: {
            locale: "en",
            fallbackLocale: "en",
            localeDir: "locales",
            enableInSFC: true
        }
    }
};
