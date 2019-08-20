import {userService} from "../_services";

import jwt_decode from "jwt-decode";

const state = {
    jwt: localStorage.getItem("t"),
    user: JSON.parse(localStorage.getItem("user")),
};

const mutations = {
    updateToken(sstate, newToken) {
        localStorage.setItem("t", newToken);
        sstate.jwt = newToken;
    },
    removeToken(sstate) {
        localStorage.removeItem("t");
        sstate.jwt = null;
    },
    updateUser(sstate, user) {
        localStorage.setItem("user", JSON.stringify(user));
        sstate.user = user;
    },
    logoutUser(sstate) {
        localStorage.removeItem("user");
        sstate.user = null;
    },
};

const actions = {
    login({commit}, credentials) {
        return userService.login(credentials.username, credentials.password)
            .then(response => {
                commit("updateToken", response.data.token);
                commit("updateUser", response.data.user);
            });
    },
    signup({commit}, credentials) {
        return userService.signup(credentials.username, credentials.password, credentials.country)
            .then(response => {
                commit("updateToken", response.data.token);
                commit("updateUser", response.data.user);
            });
    },
    logout({commit}) {
        return userService.logout()
            .then(() => {
                commit("removeToken");
                commit("logoutUser");
            });
    },
    inspectToken() {
        const token = this.state.jwt;
        if (token) {
            const decoded = jwt_decode(token);
            const exp = decoded.exp;

            if (exp - (Date.now() / 1000) < 1800 && (Date.now() / 1000) < 628200) {
                this.dispatch("refreshToken");
            } else if (exp - (Date.now() / 1000) < 1800) {
                // DO NOTHING, DO NOT REFRESH
            } else {
                // PROMPT USER TO RE-LOGIN, THIS ELSE CLAUSE COVERS THE CONDITION WHERE A TOKEN IS EXPIRED AS WELL
            }
        }
    },
};

export const account = {
    namespaced: true,
    state,
    actions,
    mutations,
};
