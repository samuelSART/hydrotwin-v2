import axios from "axios";

const API_URL = process.env.VUE_APP_API_URL || window.location.origin + "/api";

const client = axios.create({
    baseURL: API_URL
});

export type UserFormData = { email: string; password: string };
export type LogoutData = { refresh_token: string };

class AuthService {
    async execute(
        method: "get" | "post" | "put" | "delete",
        resource: string,
        data: UserFormData | LogoutData | null = null
    ) {
        return client.request({ method, url: resource, data }).then(req => {
            return req.data;
        });
    }

    verifyUser() {
        return this.execute("get", "/auth/verify");
    }

    logout() {
        return this.execute("get", "/auth/logout");
    }
}

export default new AuthService();
