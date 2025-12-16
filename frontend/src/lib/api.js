import axios from "axios";

// In development, use relative URLs so Vite proxy works
// In production, use full backend URL
const isDevelopment = import.meta.env.DEV;
const apiBaseURL = isDevelopment 
  ? "" // Empty baseURL in dev - use relative URLs, Vite proxy handles /api
  : (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000");

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

// Registration and login API calls using correct backend paths
export function registerUser(data) {
  // In dev: /api/auth/register → Vite proxy → http://localhost:8000/api/auth/register
  // In prod: baseURL + /api/auth/register → https://api.example.com/api/auth/register
  return apiClient.post('/api/auth/register', data);
}

export function loginUser(data) {
  // In dev: /api/auth/login → Vite proxy → http://localhost:8000/api/auth/login
  // In prod: baseURL + /api/auth/login → https://api.example.com/api/auth/login
  return apiClient.post('/api/auth/login', data);
}

export default apiClient;

