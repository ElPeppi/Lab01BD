import { Navigate, Outlet } from "react-router-dom";
import { useAuth, type Perfil } from "./AuthContext";

export default function RutaProtegida({ tipos }: { tipos?: Perfil["tipo"][] }) {
  const { perfil } = useAuth();

  if (!perfil) return <Navigate to="/login" replace />;
  if (tipos && !tipos.includes(perfil.tipo)) return <Navigate to="/catalogo" replace />;

  return <Outlet />;
}