<template>
    <v-card class="mx-auto rounded" tile elevation="1">
        <v-toolbar dense flat>
            <v-toolbar-title class="card-title">
                <slot name="header"></slot>
            </v-toolbar-title>

            <v-spacer></v-spacer>

            <!-- <v-btn icon>
                <v-icon>mdi-magnify</v-icon>
            </v-btn> -->
        </v-toolbar>

        <v-divider />

        <v-card-text>
            <slot name="content"></slot>
        </v-card-text>
    </v-card>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
@Component
export default class CardWidget extends Vue {}
</script>

<style lang="scss" scoped>
.card-title {
    text-align: left;
    color: #111312;
    font-weight: bold;
    font-size: 1rem;
}
</style>
