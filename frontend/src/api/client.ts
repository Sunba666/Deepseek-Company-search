import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL } from "@/constants";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor — attach JWT token
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("jobnav-auth");
    if (stored) {
      try {
        const { state } = JSON.parse(stored);
        if (state.token) {
          config.headers.Authorization = `Bearer ${state.token}`;
        }
      } catch {}
    }
  }
  return config;
});

// Response interceptor — unified error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ message: string; code: number }>) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        localStorage.removeItem("jobnav-auth");
        if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
          window.location.href = "/login";
        }
      }
      return Promise.reject(new Error(data?.message || `请求失败 (${status})`));
    }
    if (error.request) {
      return Promise.reject(new Error("网络连接失败，请检查网络"));
    }
    return Promise.reject(error);
  }
);

export default apiClient;
