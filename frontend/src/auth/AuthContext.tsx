import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import api from "../api/client";
import { tokens } from "./tokens";

export type Perfil = {
  tipo: "empleado" | "usuario";
  id: number;
  nombre: string;
  rol: string;
};

type AuthContextType = {
  perfil: Perfil | null;
  login: (correo: string, clave: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

function leerPerfil(): Perfil | null {
  try {
    const raw = localStorage.getItem("perfil");
    return raw && tokens.getAccess() ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // Al recargar la página, recupera la sesión guardada
  const [perfil, setPerfil] = useState<Perfil | null>(leerPerfil);

  // El perfil guardado en el navegador podría estar desactualizado (o el usuario bloqueado):
  // al abrir la app se confirma con el backend. Si la sesión ya no sirve, el interceptor
  // intenta renovarla y, si no puede, manda al login.
  useEffect(() => {
    if (!tokens.getAccess()) return;
    api
      .get<Perfil>("/api/auth/me/")
      .then(({ data }) => {
        localStorage.setItem("perfil", JSON.stringify(data));
        setPerfil(data);
      })
      .catch(() => {
        /* sin conexión: se conserva la sesión local; el interceptor ya maneja el 401 */
      });
  }, []);

  async function login(correo: string, clave: string) {
    const { data } = await api.post("/api/auth/login/", { correo, clave });
    tokens.set(data.access, data.refresh);
    localStorage.setItem("perfil", JSON.stringify(data.perfil));
    setPerfil(data.perfil);
  }

  function logout() {
    tokens.clear();
    setPerfil(null);
  }

  return (
    <AuthContext.Provider value={{ perfil, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// El hook vive junto al contexto a propósito; solo afecta la recarga en caliente en desarrollo.
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}