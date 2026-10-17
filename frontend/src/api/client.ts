import axios from "axios";

import { tokens } from "../auth/tokens";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    headers: {"Content-Type": "application/json"}
});

api.interceptors.request.use((config) =>{
    const token = tokens.getAccess();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const refresh = tokens.getRefresh();

    const esLoginORefresh =
      original.url?.includes("/api/auth/login") ||
      original.url?.includes("/api/auth/refresh");

    if (error.response?.status === 401 && !original._retry && refresh && !esLoginORefresh) {
      original._retry = true; // evita bucles infinitos
      try {
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/auth/refresh/`,
          { refresh }
        );
        tokens.set(data.access, data.refresh);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original); // repite la petición original con el token nuevo
      } catch {
        tokens.clear();
        window.location.href = "/login"; // refresh también venció: a login
      }
    }
    return Promise.reject(error);
  }
);

export default api;