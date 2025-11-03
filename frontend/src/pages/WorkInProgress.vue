<template>
    <v-container fill-height fluid>
        <v-row align="center" justify="center">
            <v-col class="text-center">{{ $t("wip.workInProgress") }}</v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class WorkInProgress extends Vue {}
</script>

<style scoped></style>
