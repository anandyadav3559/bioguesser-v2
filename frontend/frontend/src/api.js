
import axios from "axios";

const API_Base_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
    baseURL: API_Base_URL,
});

// Add a request interceptor to attach the token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("accessToken");
        const guestToken = localStorage.getItem("guestToken");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`; // Prefer permanent token
        } else if (guestToken) {
            config.headers.Authorization = `Bearer ${guestToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;
