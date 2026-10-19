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

// Si varias peticiones fallan con 401 a la vez (p. ej. el Inicio pide 3 cosas en paralelo),
// todas esperan el MISMO refresh en vez de pedir uno cada una.
let refrescando: Promise<string> | null = null;

function renovarAccess(refresh: string) {
  if (!refrescando) {
    refrescando = axios
      .post(`${import.meta.env.VITE_API_URL}/api/auth/refresh/`, { refresh })
      .then(({ data }) => {
        tokens.set(data.access, data.refresh);
        return data.access as string;
      })
      .finally(() => {
        refrescando = null;
      });
  }
  return refrescando;
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const refresh = tokens.getRefresh();

    const esLoginORefresh =
      original?.url?.includes("/api/auth/login") ||
      original?.url?.includes("/api/auth/refresh");

    if (error.response?.status === 401 && original && !original._retry && refresh && !esLoginORefresh) {
      original._retry = true; // evita bucles infinitos
      try {
        const access = await renovarAccess(refresh);
        original.headers.Authorization = `Bearer ${access}`;
        return api(original); // repite la petición original con el token nuevo
      } catch {
        tokens.clear();
        window.location.href = "/login"; // el refresh también venció: a login
      }
    }
    return Promise.reject(error);
  }
);

export default api;
