<template>
    <v-app>
        <v-container class="container--fluid fill-height primary">
            <v-row no-gutters align="center" justify="center">
                <v-col cols="12" sm="8" md="4" lg="4">
                    <v-form @keyup.native.enter="login">
                        <v-card class="elevation-5 pa-3">
                            <v-card-text>
                                <div class="layout column align-center mb-5">
                                    <v-img
                                        src="@/assets/img/logo_ht.png"
                                        alt="HydroTwin Logo"
                                    />
                                </div>

                                <v-divider class="my-2"></v-divider>

                                <div class="layout column align-center">
                                    <Transition name="fade" mode="out-in">
                                        <div
                                            class="my-3"
                                            v-if="loading"
                                            key="spinner"
                                        >
                                            <v-progress-circular
                                                :width="3"
                                                color="primary"
                                                indeterminate
                                            />
                                        </div>
                                        <div
                                            class="my-3"
                                            v-if="!loading"
                                            key="icon"
                                        >
                                            <v-icon
                                                x-large
                                                :color="stateIconColor"
                                            >
                                                {{ stateIconId }}
                                            </v-icon>
                                        </div>
                                    </Transition>
                                    <div class="text-caption mt-3">
                                        {{ stateMessage }}
                                    </div>
                                </div>
                            </v-card-text>
                            <v-card-actions>
                                <v-btn
                                    color="primary"
                                    width="100%"
                                    :disabled="buttonDisabled"
                                    @click="login"
                                >
                                    {{ $t("signIn.signIn") }}
                                </v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-form>
                </v-col>
            </v-row>
        </v-container>
    </v-app>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapActions } from "vuex";
import { i18n } from "@/plugins/i18n";

import { sleep } from "@/utils";
import * as types from "@/store/types";
import { VerificationStatus } from "@/store/modules/auth";

enum LoginState {
    Error,
    Unauthorized,
    Verified,
    Verifying
}

const textMessages = new Map<
    LoginState,
    {
        text: string;
        icon: string;
        color: string;
    }
>([
    [
        LoginState.Error,
        { text: `${i18n.t("auth.error")}`, color: "red", icon: "mdi-cancel" }
    ],
    [
        LoginState.Unauthorized,
        {
            text: `${i18n.t("auth.unauthorized")}`,
            color: "red",
            icon: "mdi-cancel"
        }
    ],
    [
        LoginState.Verified,
        {
            text: `${i18n.t("auth.verified")}`,
            color: "green",
            icon: "mdi-check"
        }
    ],
    [
        LoginState.Verifying,
        {
            text: `${i18n.t("auth.verifying")}`,
            color: "green",
            icon: "mdi-checkbox-circle"
        }
    ]
]);

@Component({
    methods: {
        ...mapActions({
            authVerify: types.AUTH_VERIFY
        })
    }
})
export default class SigninForm extends Vue {
    authVerify!: () => Promise<VerificationStatus>;
    userRoles!: string[];

    loading = true;

    state: LoginState = LoginState.Verifying;
    casURL: string | undefined = undefined;

    async mounted() {
        this.loading = true;
        this.state = LoginState.Verifying;

        await sleep(500);

        const verificationStatus: VerificationStatus | void = await this.authVerify()
            .catch((e: VerificationStatus) => {
                console.error("error user verify", e);

                if (e.state === "unauthorized") {
                    this.state = LoginState.Unauthorized;
                    this.casURL = e.casURL;

                    return;
                }

                this.state = LoginState.Error;
            })
            .finally(() => {
                this.loading = false;
            });

        if (!verificationStatus || verificationStatus.state !== "verified")
            return;

        this.state = LoginState.Verified;

        await sleep(1000);

        this.goTo("/");
    }

    /**
     * Redirect user to CHS login webpage
     */
    async login() {
        if (!this.casURL) return;

        this.loading = true;

        await sleep(500);

        window.location.assign(this.casURL);
    }

    goTo(route: string) {
        this.$router.push(route);
    }

    get buttonDisabled() {
        return this.state !== LoginState.Unauthorized || this.loading;
    }

    get stateMessage() {
        return textMessages.get(this.state)?.text || "";
    }

    get stateIconId() {
        return textMessages.get(this.state)?.icon || undefined;
    }

    get stateIconColor() {
        return textMessages.get(this.state)?.color || "white";
    }
}
</script>

<style lang="scss" scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.25s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
    opacity: 0;
}
</style>
