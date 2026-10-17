import {Link, Outlet} from "react-router-dom";

export default function Layout(){

    return(
        <div>
            <nav>
                <Link to="/">Dashboard</Link>
                <Link to="/ejemplares">Ejemplares</Link>
                <Link to="/catalogo">Catálogo</Link>
                <Link to="/prestamos">Préstamos</Link>
            </nav>

            <main>
                <Outlet />
            </main>
        </div>
    );

}