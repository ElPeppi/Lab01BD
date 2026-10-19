import { Suspense, useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { Cargando } from "./Estados";
import "./Layout.css";

type ItemMenu = { to: string; texto: string };

// El menú depende del tipo de cuenta. Ocultar una opción NO es seguridad:
// la protección real está en RutaProtegida y en los permisos del backend.
const MENU_EMPLEADO: ItemMenu[] = [
  { to: "/dashboard", texto: "Inicio" },
  { to: "/catalogo", texto: "Catálogo" },
  { to: "/ejemplares", texto: "Ejemplares" },
  { to: "/prestamos", texto: "Préstamos" },
  { to: "/devoluciones", texto: "Devoluciones" },
  { to: "/multas", texto: "Multas" },
  { to: "/reportes", texto: "Reportes" },
];

const MENU_USUARIO: ItemMenu[] = [
  { to: "/catalogo", texto: "Catálogo" },
  { to: "/prestamos", texto: "Mis préstamos" },
  { to: "/multas", texto: "Mis multas" },
];

const NOMBRE_ROL: Record<string, string> = {
  admin: "Administrador",
  bibliotecario: "Bibliotecario",
  estudiante: "Estudiante",
  docente: "Docente",
};

export default function Layout() {
  const { perfil, logout } = useAuth();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const menu = perfil?.tipo === "empleado" ? MENU_EMPLEADO : MENU_USUARIO;
  const cerrarMenu = () => setMenuAbierto(false);

  // Con el menú abierto en celular: Escape lo cierra y la página de atrás no hace scroll
  useEffect(() => {
    if (!menuAbierto) return;
    const alPresionar = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMenuAbierto(false);
    };
    document.addEventListener("keydown", alPresionar);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", alPresionar);
      document.body.style.overflow = "";
    };
  }, [menuAbierto]);

  return (
    <div className="app">
      {/* Barra superior: solo se ve en celular */}
      <header className="app-barra">
        <button
          type="button"
          className="app-hamburguesa"
          aria-label="Abrir menú"
          aria-expanded={menuAbierto}
          aria-controls="menu-lateral"
          onClick={() => setMenuAbierto(true)}
        >
          <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">
            <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>
        <p className="app-marca">BibliotecaUN</p>
      </header>

      {/* Fondo oscuro detrás del menú abierto; tocarlo cierra el menú */}
      <div
        className={`app-fondo${menuAbierto ? " visible" : ""}`}
        onClick={cerrarMenu}
        aria-hidden="true"
      />

      <aside id="menu-lateral" className={`app-lateral${menuAbierto ? " abierto" : ""}`}>
        <div className="app-lateral-cabecera">
          <p className="app-marca">BibliotecaUN</p>
          <button type="button" className="app-cerrar" aria-label="Cerrar menú" onClick={cerrarMenu}>
            <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <nav className="app-menu" aria-label="Menú principal">
          {menu.map((item) => (
            <NavLink key={item.to} to={item.to} className="app-enlace" onClick={cerrarMenu}>
              {item.texto}
            </NavLink>
          ))}
        </nav>

        <div className="app-sesion">
          <p className="app-usuario">{perfil?.nombre}</p>
          <p className="app-rol">{NOMBRE_ROL[perfil?.rol ?? ""] ?? perfil?.rol}</p>
          <button type="button" className="app-salir" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="app-contenido">
        {/* Mientras llega el código de la pantalla (lazy), el menú sigue visible */}
        <Suspense fallback={<Cargando />}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}
