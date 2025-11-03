import Vue from "vue";
import Vuex from "vuex";

import * as types from "./types";
import auth from "./modules/auth";

Vue.use(Vuex);

interface InfoMessage {
    shown: boolean;
    text: string | null;
}

interface AppState {
    drawer: boolean | null;
    progressbar: boolean;
    filterLoading: boolean;
    infoMessage: InfoMessage;
}

const appState: AppState = {
    drawer: null,
    progressbar: false,
    filterLoading: false,
    infoMessage: {
        shown: false,
        text: null
    }
};

const state = {
    app: appState
};

export default new Vuex.Store({
    state: state,

    mutations: {
        [types.MUTATE_APP_DRAWER](state: State, drawer: boolean | null) {
            state.app.drawer = drawer;
        },

        [types.MUTATE_APP_PROGRESSBAR](
            state: State,
            progressbarState: boolean
        ) {
            state.app.progressbar = progressbarState;
        },

        [types.MUTATE_APP_FILTER_LOADING](
            state: State,
            filterLoadingState: boolean
        ) {
            state.app.filterLoading = filterLoadingState;
        },

        [types.MUTATE_APP_INFO_MESSAGE](
            state: State,
            infoMessage: InfoMessage
        ) {
            state.app.infoMessage.shown = infoMessage.shown;
            state.app.infoMessage.text = infoMessage.text;
        }
    },

    actions: {},

    getters: {
        [types.APP_DRAWER](state: State) {
            return state.app.drawer;
        },

        [types.APP_PROGRESSBAR](state: State) {
            return state.app.progressbar;
        },

        [types.APP_FILTER_LOADING](state: State) {
            return state.app.filterLoading;
        },

        [types.APP_INFO_MESSAGE](state: State) {
            return state.app.infoMessage;
        }
    },

    modules: {
        auth
    }
});

type State = typeof state;
