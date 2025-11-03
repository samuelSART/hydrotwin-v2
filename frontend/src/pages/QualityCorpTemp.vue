<template>
    <v-container fill-height fluid>
        <v-row align="center" justify="center">
            <v-card
                class="mx-auto my-12"
                max-width="70%"
                elevation="0"
                color="#FAFAFA"
            >
                <template slot="progress">
                    <v-progress-linear
                        color="deep-purple"
                        height="10"
                        indeterminate
                    ></v-progress-linear>
                </template>

                <v-img
                    height="100%"
                    contain
                    src="@/assets/img/quality_corp.jpg"
                ></v-img>

                <v-card-text class="text-body-2">
                    <div class="text-center black--text">
                        {{ "- " + $t("wip.deployment") + " -" }}
                    </div>
                </v-card-text>
            </v-card>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class QualitySaicaTemp extends Vue {}
</script>
