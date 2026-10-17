import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { isAxiosError } from "axios";
import { useAuth } from "../../auth/AuthContext";

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
        setError("No hay conexión con el servidor.");
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <main style={{ maxWidth: 360, margin: "80px auto", padding: 16 }}>
      <h1>BibliotecaUN</h1>
      <form onSubmit={onSubmit}>
        <label>
          Correo
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required autoFocus />
        </label>
        <label>
          Contraseña
          <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} required />
        </label>
        {error && <p role="alert" style={{ color: "crimson" }}>{error}</p>}
        <button type="submit" disabled={cargando}>
          {cargando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </main>
  );
}