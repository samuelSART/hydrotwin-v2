<template>
    <v-app>
        <AppBar />
        <Drawer />
        <MainView />
    </v-app>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component({
    components: {
        AppBar: () => import("@/components/layout/AppBar.vue"),
        MainView: () => import("@/components/layout/MainView.vue"),
        Drawer: () => import("@/components/layout/Drawer.vue")
    }
})
export default class Index extends Vue {}
</script>
