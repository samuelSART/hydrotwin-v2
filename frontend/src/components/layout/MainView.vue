<template>
    <v-main class="grey lighten-5">
        <ProgressBar />
        <InfoSnackbar />
        <router-view />
        <Footer />
    </v-main>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component({
    components: {
        ProgressBar: () => import("@/components/layout/ProgressBar.vue"),
        InfoSnackbar: () => import("@/components/layout/InfoSnackbar.vue"),
        Footer: () => import("@/components/layout/Footer.vue")
    }
})
export default class MainView extends Vue {}
</script>

<style></style>
