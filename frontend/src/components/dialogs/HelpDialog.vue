<template>
    <v-dialog v-model="shown" width="80%">
        <v-card>
            <v-card-title class="text-h5 grey lighten-2">
                {{ $t("appBar.help") }}
            </v-card-title>

            <v-card-text class="mt-2">
                <div v-html="htmlContent"></div>
            </v-card-text>

            <v-divider></v-divider>

            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" text @click="shown = false">
                    {{ $t("appBar.ok") }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, ModelSync, Prop } from "vue-property-decorator";

@Component
export default class HelpDialog extends Vue {
    @ModelSync("shownValue", "change", { type: Boolean })
    shown!: boolean;

    @Prop({ type: String, required: true, default: "" })
    htmlContent!: string;
}
</script>

<style scoped></style>
