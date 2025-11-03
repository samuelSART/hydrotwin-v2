<template>
    <v-snackbar v-model="snackbar" bottom color="primary">
        {{ infoText }}
        <template v-slot:action="{ attrs }">
            <v-btn
                color="white"
                outlined
                v-bind="attrs"
                @click="snackbar = false"
            >
                Close
            </v-btn>
        </template>
    </v-snackbar>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import { mapGetters, mapMutations } from "vuex";

import * as types from "@/store/types";

@Component({
    methods: {
        ...mapMutations({
            setInfoMessage: types.MUTATE_APP_INFO_MESSAGE
        })
    },
    computed: {
        ...mapGetters({
            getInfoMessage: types.APP_INFO_MESSAGE
        })
    }
})
export default class InfoSnackbar extends Vue {
    setInfoMessage!: (state: { shown: boolean; text: string | null }) => void;
    getInfoMessage!: { shown: boolean; text: string | null };

    get snackbar() {
        return this.getInfoMessage.shown;
    }

    set snackbar(val) {
        this.setInfoMessage({ shown: val, text: null });
    }

    get infoText() {
        return this.getInfoMessage.text;
    }
}
</script>

<style></style>
