<template>
    <div>
        <!-- checkbox activator-->
        <div class="d-flex flex-row">
            <div class="align-self-center">
                <v-checkbox
                    v-model="activated"
                    :disabled="!enabled"
                    dense
                ></v-checkbox>
            </div>
            <div class="align-self-center mr-2">
                {{ labelText }}
            </div>
        </div>

        <!-- selector -->
        <v-card
            :disabled="!activated || !enabled"
            tile
            elevation="0"
            color="#e8e8e8"
        >
            <v-card-text class="pa-1 px-3">
                <v-subheader class="pa-0 mt-2" style="height:auto">
                    {{ subheaderText }}
                </v-subheader>
                <v-select
                    dense
                    :items="options"
                    item-text="text"
                    item-value="value"
                    :value="defaultOption"
                    @change="handleChange"
                ></v-select>
            </v-card-text>
        </v-card>
    </div>
</template>

<script lang="ts">
import { Component, Vue, ModelSync, Prop, Watch } from "vue-property-decorator";
import { ComboBoxItem } from "@/interfaces";

@Component
export default class SelectActivator extends Vue {
    @ModelSync("activatedValue", "change", { type: Boolean })
    activated!: boolean;

    @Prop({ type: Boolean, required: false, default: true })
    enabled!: boolean;

    @Prop({ type: Number, required: true, default: 0 })
    defaultOption!: number;

    @Prop({ type: Array, required: false, default: null })
    options!: ComboBoxItem[] | null;

    @Prop({ type: String, required: false, default: "" })
    labelText!: string;

    @Prop({ type: String, required: false, default: "" })
    subheaderText!: string;

    /**
     * Force deactivate checkbox if not enabled
     */
    @Watch("enabled")
    onEnabledChaged() {
        if (!this.enabled) this.activated = false;
    }

    handleChange(value: number) {
        this.$emit("on-selected", value);
    }
}
</script>

<style scoped></style>
