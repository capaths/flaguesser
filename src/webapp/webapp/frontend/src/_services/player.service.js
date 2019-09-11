import axios from "axios";

const GATEWAY_URI = process.env.GATEWAY_URI || "http://localhost:8000/";

function getOnlineUsers() {
    return axios({
        method: "get",
        url: `${GATEWAY_URI}/online_users`,
    });
}

function login(username, password) {
    const payload = {
        username: username,
        password: password,
    };

    return axios({
        method: "post",
        url: `${GATEWAY_URI}/login`,
        data: payload,
    });
}

function signup(username, password, country) {
    const payload = {
        username: username,
        password: password,
        country: country,
    };

    return axios({
        method: "post",
        url: `${GATEWAY_URI}/signup`,
        data: payload,
    });
}

function logout() {
    const payload = {
        jwt: localStorage.getItem("t"),
    };

    return axios({
        method: "post",
        url: `${GATEWAY_URI}/logout`,
        data: payload,
    });
}

export const userService = {
    login,
    logout,
    signup,
    getOnlineUsers,
};
