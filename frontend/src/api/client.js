import axios from "axios";
import { useAuthStore } from "../stores/authStore";

const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor: handle 401s (token refresh), 500s, and network errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't retried yet — try token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const {
          refreshToken: currentRefresh,
          setTokens,
          logout,
        } = useAuthStore.getState();

        if (!currentRefresh) {
          logout();
          return Promise.reject(error);
        }

        // Try to refresh
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: currentRefresh,
        });

        const { access_token } = response.data;

        // Update store with new token (keep old refresh token)
        setTokens(access_token, currentRefresh);

        // Retry original request with new token
        originalRequest.headers["Authorization"] = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed — force logout
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }

    // Handle non-401 errors globally — log for observability
    if (!error.response) {
      // Network error: offline, DNS failure, CORS block, etc.
      console.error("[API] Network error — server unreachable");
    } else if (error.response.status >= 500) {
      console.error("[API] Server error:", error.response.status, error.response.data);
    }

    return Promise.reject(error);
  },
);

export default apiClient;
