import axios from "axios";

// Get API base URL from environment variable, with fallback
const apiBaseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: apiBaseURL,
  headers: {
    "Content-Type": "application/json"
  }
});

// Add request interceptor to include Authorization header with token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if needed
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      // You can add redirect logic here if you have a login page
      console.error("Authentication failed. Please login again.");
    }
    return Promise.reject(error);
  }
);

export default apiClient;

