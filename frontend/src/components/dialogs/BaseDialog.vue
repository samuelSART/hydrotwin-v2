<template>
    <v-dialog v-model="shown" width="80%" @input="handleInput">
        <v-card>
            <v-card-title>
                <span class="text-h5">{{ title }}</span>
            </v-card-title>

            <v-card-subtitle>
                <div class="mt-2">{{ subtitle }}</div>
            </v-card-subtitle>

            <v-sheet v-if="$slots.form" class="mx-6 mb-5 pa-6" outlined>
                <slot name="form"></slot>
            </v-sheet>

            <v-divider class="mx-6"></v-divider>

            <v-card-text>
                <!-- Loading spinner -->
                <div v-show="loading" style="height:450px" class="text-center">
                    <v-container fill-height fluid>
                        <v-row align="center" justify="center">
                            <v-col>
                                <v-progress-circular
                                    :width="3"
                                    color="primary"
                                    indeterminate
                                ></v-progress-circular>
                            </v-col>
                        </v-row>
                    </v-container>
                </div>

                <!-- Plot -->
                <div v-show="!loading" class="my-4">
                    <slot name="plot"></slot>
                </div>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script lang="ts">
import { Component, ModelSync, Prop, Vue } from "vue-property-decorator";

@Component
export default class BaseDialog extends Vue {
    @ModelSync("shownValue", "change", { type: Boolean })
    shown!: boolean;

    @Prop({ type: String, required: false, default: "" })
    title!: string;

    @Prop({ type: String, required: false, default: "" })
    subtitle!: string;

    @Prop({ type: Boolean, required: false, default: false })
    loading!: boolean;

    handleInput(activated: boolean) {
        if (!activated) this.$emit("on-close");
    }
}
</script>

<style scoped></style>
