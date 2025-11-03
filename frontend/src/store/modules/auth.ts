import AuthService from "@/services/auth/auth-service";
import {
    UserData,
    UserRole,
    LoginVerificationResponse,
    ResponseError,
    LogoutResponse
} from "@/interfaces";
import * as types from "../types";
import router from "@/router";

export interface UserState {
    status: { loggedIn: boolean };
    user: UserData | null;
}

export interface VerificationStatus {
    state: "verified" | "error" | "unauthorized";
    casURL?: string;
}

type VerificationError = { cas_url: string } & ResponseError;

const getRawUserState = (): UserState => {
    return { status: { loggedIn: false }, user: null };
};

const userState: UserState = getRawUserState();
const userRoles: UserRole[] = [
    { text: "Client", value: "client" },
    { text: "Technical", value: "technical" },
    { text: "Administrator", value: "admin" }
];

/**
 * Auth store module
 */
const state = {
    userState,
    userRoles
};

const auth = {
    state: state,

    mutations: {
        [types.MUTATE_USER_STATE](state: State, userState: UserState) {
            state.userState = userState;
        }
    },

    actions: {
        async [types.AUTH_VERIFY]({ commit }) {
            const verificationState: VerificationStatus = {
                state: "error"
            };

            const verifyRes: LoginVerificationResponse = await AuthService.verifyUser().catch(
                e => {
                    if (
                        e.response &&
                        e.response.data &&
                        "cas_url" in e.response.data
                    ) {
                        throw {
                            ...verificationState,
                            state: "unauthorized",
                            casURL: e.response.data.cas_url
                        };
                    }

                    throw {
                        ...verificationState,
                        state: "error"
                    };
                }
            );

            if (!verifyRes || !verifyRes.ok) return verificationState;

            const userName = verifyRes.data.username;
            commit(types.MUTATE_USER_STATE, {
                status: { loggedIn: true },
                user: {
                    name: userName
                }
            });

            return {
                ...verificationState,
                state: "verified"
            };
        },

        async [types.AUTH_LOGOUT]({ commit }) {
            commit(types.MUTATE_USER_STATE, getRawUserState());

            const logoutRes: LogoutResponse = await AuthService.logout();

            if (!logoutRes || !logoutRes.ok) {
                commit(types.MUTATE_USER_STATE, {
                    ...getRawUserState()
                });
                router.push("/signin");
                return;
            }

            const data = logoutRes.data;
            if (data && data.cas_logout_url) {
                commit(types.MUTATE_USER_STATE, {
                    ...getRawUserState()
                });
                router.push("/signin");
                window.open(data.cas_logout_url);
            }
        }
    },

    getters: {
        [types.AUTH_USERNAME](state: State) {
            return state.userState.user?.name
                ? `${state.userState.user?.name}`
                : undefined;
        },

        [types.AUTH_USER_ROLES](state: State) {
            return state.userRoles;
        }
    }
};

export default auth;

type State = typeof state;
