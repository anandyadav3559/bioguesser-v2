
import axios from "axios";

const API_Base_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
    baseURL: API_Base_URL,
});

// Attach stored token to every request
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

// Handle 401s globally — backend rejected our token (Redis session expired/deleted).
// Clear the stale token so ProtectedRoute redirects to login instead of showing a broken app.
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("accessToken");
            localStorage.removeItem("guestToken");
            // Only redirect if we're not already on the login page
            if (window.location.pathname !== "/") {
                window.location.href = "/";
            }
        }
        return Promise.reject(error);
    }
);

export default api;
