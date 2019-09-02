import axios from "axios";

function login(username, password) {
    const payload = {
        username: username,
        password: password,
    };

    return axios({
        method: "post",
        url: "http://localhost:8000/login",
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
        url: "http://localhost:8000/signup",
        data: payload,
    });
}

function logout() {
    const payload = {
        jwt: localStorage.getItem("t"),
    };

    return axios({
        method: "post",
        url: "http://localhost:8000/logout",
        data: payload,
    });
}

export const userService = {
    login,
    logout,
    signup,
};
