/* FocusFlow API layer — talks to the FastAPI backend on port 8000. */

const API_BASE_URL = "http://127.0.0.1:8001";
const TOKEN_KEY = "access_token";

class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(value) {
    localStorage.setItem(TOKEN_KEY, value);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function detailOf(data) {
    if (!data) return "";
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map((item) => item.msg || JSON.stringify(item)).join(" ");
    }
    if (typeof data.message === "string") return data.message;
    return "";
}

async function request(path, options = {}) {
    const method = options.method || "GET";
    const auth = options.auth !== false;
    const headers = {};
    let body;

    if (auth) {
        const token = getToken();
        if (token) headers.Authorization = "Bearer " + token;
    }

    if (options.form) {
        headers["Content-Type"] = "application/x-www-form-urlencoded";
        body = new URLSearchParams(options.form).toString();
    } else if (options.body !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(options.body);
    }

    let response;
    try {
        response = await fetch(API_BASE_URL + path, { method, headers, body });
    } catch (error) {
        throw new ApiError(
            "We couldn't reach the server. Check that the backend is running on port 8001, then try again.",
            0
        );
    }

    let data = null;
    try {
        data = await response.json();
    } catch (error) {
        data = null;
    }

    if (response.status === 401 && getToken()) {
        clearToken();
        if (!/login\.html$|register\.html$/.test(window.location.pathname)) {
            window.location.href = "login.html";
        }
        throw new ApiError("Your session ended. Sign in again.", 401);
    }

    if (!response.ok) {
        throw new ApiError(
            detailOf(data) || "The server could not complete that request (" + response.status + ").",
            response.status
        );
    }

    return data;
}

const API = {
    login(email, password) {
        return request("/users/login", {
            method: "POST",
            form: { username: email, password: password },
            auth: false
        });
    },

    register(payload) {
        return request("/users/", { method: "POST", body: payload, auth: false });
    },

    me() {
        return request("/users/me");
    },

    users() {
        return request("/users/");
    },

    deleteUser(userId) {
        return request("/users/" + userId, { method: "DELETE" });
    },

    projects() {
        return request("/projects/");
    },

    createProject(payload) {
        return request("/projects/", { method: "POST", body: payload });
    },

    updateProject(projectId, payload) {
        return request("/projects/" + projectId, { method: "PUT", body: payload });
    },

    deleteProject(projectId) {
        return request("/projects/" + projectId, { method: "DELETE" });
    },

    tasks() {
        return request("/tasks/");
    },

    createTask(payload) {
        return request("/tasks/", { method: "POST", body: payload });
    },

    updateTask(taskId, payload) {
        return request("/tasks/" + taskId, { method: "PUT", body: payload });
    },

    deleteTask(taskId) {
        return request("/tasks/" + taskId, { method: "DELETE" });
    }
};
