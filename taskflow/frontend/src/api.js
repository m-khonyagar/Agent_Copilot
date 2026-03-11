import axios from "axios";

const BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const tasksApi = {
  getAll: () => api.get("/api/tasks"),
  getById: (taskId) => api.get(`/api/tasks/${taskId}`),
  create: (goal) => api.post("/api/tasks", { goal }),
  delete: (taskId) => api.delete(`/api/tasks/${taskId}`),
  cancel: (taskId) => api.post(`/api/tasks/${taskId}/cancel`),
};

export const artifactsApi = {
  browse: (taskId) => api.get(`/api/artifacts/${taskId}/browse`),
  download: (taskId, filePath) =>
    `${BASE_URL}/api/artifacts/${taskId}/download?path=${encodeURIComponent(filePath)}`,
};

export const createWebSocket = (taskId) => {
  const wsBase = BASE_URL.replace(/^http/, "ws");
  return new WebSocket(`${wsBase}/ws/${taskId}`);
};

export default api;
