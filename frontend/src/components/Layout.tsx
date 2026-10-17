import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Layout() {
    const { perfil, logout } = useAuth();
    return (
        <div>
            <nav>
                <Link to="/">Dashboard</Link>
                <Link to="/ejemplares">Ejemplares</Link>
                <Link to="/catalogo">Catálogo</Link>
                <Link to="/prestamos">Préstamos</Link>
                <span>{perfil?.nombre} · {perfil?.rol}</span>
                <button onClick={logout}>Cerrar sesión</button>
            </nav>

            <main>
                <Outlet />
            </main>
        </div>
    );

}