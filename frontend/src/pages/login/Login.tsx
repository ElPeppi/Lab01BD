import { useState, type CSSProperties, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { isAxiosError } from "axios";
import { useAuth } from "../../auth/AuthContext";
import "./Login.css";

// Fechas decorativas de la ficha de préstamo (la última es la que se anima)
const SELLOS = [
  { fecha: "12 MAR 2025", giro: -2, x: "0.5rem" },
  { fecha: "03 SEP 2025", giro: 1.5, x: "1.75rem" },
  { fecha: "28 ABR 2026", giro: -1, x: "0.75rem" },
  { fecha: "24 OCT 2026", giro: 2.5, x: "2.25rem" },
];

export default function Login() {
  const { perfil, login } = useAuth();
  const [correo, setCorreo] = useState("");
  const [clave, setClave] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  // Si ya hay sesión (o el login acaba de funcionar), redirige según el tipo
  if (perfil) {
    return <Navigate to={perfil.tipo === "empleado" ? "/dashboard" : "/catalogo"} replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault(); // evita que el form recargue la página
    setError("");
    setCargando(true);
    try {
      await login(correo, clave);
    } catch (err) {
      if (isAxiosError(err) && err.response) {
        setError(err.response.data?.error ?? "No se pudo iniciar sesión.");
      } else {
        setError("No hay conexión con el servidor. Revisa que el backend esté encendido.");
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="login">
      <aside className="login-portada">
        <p className="login-marca">BibliotecaUN</p>

        {/* Decorativo: los lectores de pantalla lo ignoran */}
        <div className="ficha" aria-hidden="true">
          <div className="ficha-cabecera">
            <span>Biblioteca universitaria</span>
            <span>Fecha de devolución</span>
          </div>
          <ol className="ficha-sellos">
            {SELLOS.map((s, i) => (
              <li key={s.fecha} style={{ "--x": s.x } as CSSProperties}>
                <span
                  className={i === SELLOS.length - 1 ? "sello sello--nuevo" : "sello"}
                  style={{ "--giro": `${s.giro}deg` } as CSSProperties}
                >
                  {s.fecha}
                </span>
              </li>
            ))}
            <li />
            <li />
          </ol>
        </div>

        <p className="login-lema">Consulta el catálogo y solicita tus préstamos en línea.</p>
      </aside>

      <main className="login-formulario">
        <div className="login-caja">
          <h1>Inicia sesión</h1>
          <p className="login-intro">Entra con tu correo institucional.</p>

          <form onSubmit={onSubmit}>
            <div className="campo">
              <label htmlFor="correo">Correo</label>
              <input
                id="correo"
                type="email"
                autoComplete="username"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div className="campo">
              <label htmlFor="clave">Contraseña</label>
              <input
                id="clave"
                type="password"
                autoComplete="current-password"
                value={clave}
                onChange={(e) => setClave(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="alerta alerta--error" role="alert">
                {error}
              </div>
            )}

            <button type="submit" className="btn btn--bloque" disabled={cargando}>
              {cargando ? "Ingresando…" : "Ingresar"}
            </button>
          </form>

          <p className="login-ayuda">
            ¿No puedes entrar? Acércate al mostrador de la biblioteca para revisar tu cuenta.
          </p>
        </div>
      </main>
    </div>
  );
}
