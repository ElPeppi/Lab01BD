import { Navigate, Outlet } from "react-router-dom";
import { useAuth, type Perfil } from "./AuthContext";

export default function RutaProtegida({ tipos, roles }: { tipos?: Perfil["tipo"][]; roles?: string[] }) {
  const { perfil } = useAuth();

  if (!perfil) return <Navigate to="/login" replace />;
  if (tipos && !tipos.includes(perfil.tipo)) return <Navigate to="/catalogo" replace />;
  if (roles && !roles.includes(perfil.rol)) return <Navigate to="/catalogo" replace />;

  return <Outlet />;
}