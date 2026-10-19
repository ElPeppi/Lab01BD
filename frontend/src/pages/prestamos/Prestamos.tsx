import { useAuth } from "../../auth/AuthContext";
import GestionPrestamos from "./GestionPrestamos";
import MisPrestamos from "./MisPrestamos";

/** Una sola ruta (/prestamos), dos vistas según quién entra. */
export default function Prestamos() {
  const { perfil } = useAuth();
  return perfil?.tipo === "empleado" ? <GestionPrestamos /> : <MisPrestamos />;
}
