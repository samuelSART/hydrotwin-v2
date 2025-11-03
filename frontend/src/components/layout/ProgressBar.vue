<template>
    <v-progress-linear
        indeterminate
        striped
        height="5"
        color="primary"
        :active="progressState"
        absolute
    ></v-progress-linear>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import { mapGetters } from "vuex";

import * as types from "@/store/types";

@Component({
    computed: {
        ...mapGetters({
            progressState: types.APP_PROGRESSBAR
        })
    }
})
export default class ProgressBar extends Vue {}
</script>

<style></style>
