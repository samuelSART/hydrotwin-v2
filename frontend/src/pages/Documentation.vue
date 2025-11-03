<template>
    <v-container fluid>
        <v-row>
            <v-col>
                <ul>
                    <li
                        class="my-2"
                        v-for="{ title, url } in lines"
                        :key="title"
                    >
                        <a color="primary" :href="url" target="_blank">
                            {{ title }}
                        </a>
                    </li>
                </ul>
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Documentation extends Vue {
    lines = [
        {
            title: `${this.$t("line")} 1`,
            url:
                "https://grusamar.com/hydrotwin/documentacion/manuales/Manual_L1_mar23_v1.0.pdf"
        },
        {
            title: `${this.$t("line")} 2`,
            url:
                "https://grusamar.com/hydrotwin/documentacion/manuales/Manual_L2_mar23_v1.0.pdf"
        },
        {
            title: `${this.$t("line")} 3`,
            url:
                "https://grusamar.com/hydrotwin/documentacion/manuales/Manual_L3_mar23_v1.0.pdf"
        },
        {
            title: `${this.$t("line")} 4`,
            url:
                "https://grusamar.com/hydrotwin/documentacion/manuales/Manual_L4_mar23_v1.0.pdf"
        },
        {
            title: `${this.$t("line")} 5`,
            url:
                "https://grusamar.com/hydrotwin/documentacion/manuales/Manual_L5_mar23_v1.0.pdf"
        },
        {
            title: `${this.$t("line")} 6`,
            url:
                "https://grusamar.com/hydrotwin/documentacion/manuales/Manual_L6_mar23_v1.0.pdf"
        }
    ];
}
</script>

<style scoped></style>
