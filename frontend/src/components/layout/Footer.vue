<template>
    <v-footer fixed class="pa-0 ma-0" style="height: 64px;">
        <v-col class="text-right text-caption pa-0 ma-5">
            &copy; HydroTwin {{ new Date().getFullYear() }} ({{ version }})
        </v-col>
        <div class="d-flex">
            <v-img
                alt="CDTI"
                class="shrink mr-2 ml-0"
                contain
                src="@/assets/img/CDTI.png"
                transition="scale-transition"
                width="200"
            />
            <v-img
                alt="FEDER"
                class="shrink mr-2 ml-0"
                contain
                src="@/assets/img/FEDER.png"
                transition="scale-transition"
                width="150"
            />
        </div>
    </v-footer>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Footer extends Vue {
    version = process.env.VUE_APP_VERSION || "nover";
}
</script>
