import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { usuariosApi } from "../../api/usuarios";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EtiquetaEstado } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { useDebounce } from "../../hooks/useDebounce";
import { plural } from "../../utils/formato";
import FormUsuario from "./FormUsuario";

/** Solo el administrador: registra estudiantes y docentes y abre el historial de cada uno. */
export default function Usuarios() {
  const [texto, setTexto] = useState("");
  const q = useDebounce(texto.trim(), 300);
  const consulta = useCallback(() => usuariosApi.listar(q), [q]);
  const usuarios = useConsulta(consulta);

  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [registrando, setRegistrando] = useState(false);

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Usuarios</h1>
          <p>
            {usuarios.datos
              ? `${plural(usuarios.datos.length, "usuario")}${q ? " con esta búsqueda" : " registrados"}.`
              : "Estudiantes y docentes que pueden pedir préstamos."}
          </p>
        </div>
        <button type="button" className="btn" onClick={() => setRegistrando(true)}>
          Registrar usuario
        </button>
      </header>

      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <div className="campo campo--ancho">
          <label htmlFor="buscar-usuario">Buscar</label>
          <input
            id="buscar-usuario"
            type="search"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Nombre, código o correo"
          />
        </div>
      </form>

      <Aviso aviso={aviso} onCerrar={() => setAviso(null)} />

      {usuarios.error && <ErrorCarga mensaje={usuarios.error} onReintentar={usuarios.recargar} />}
      {!usuarios.datos && usuarios.cargando && <Cargando texto="Cargando usuarios…" />}

      {usuarios.datos && usuarios.datos.length === 0 && (
        <Vacio titulo={q ? "Ningún usuario coincide" : "Aún no hay usuarios"}>
          <p>{q ? "Prueba con otro nombre, código o correo." : "Registra el primero para que pueda pedir préstamos."}</p>
        </Vacio>
      )}

      {usuarios.datos && usuarios.datos.length > 0 && (
        <div className="tabla-contenedor">
          <table className="tabla" aria-busy={usuarios.cargando}>
            <thead>
              <tr>
                <th scope="col">Nombre</th>
                <th scope="col">Código</th>
                <th scope="col">Identificación</th>
                <th scope="col">Tipo</th>
                <th scope="col">Estado</th>
                <th scope="col"><span className="sr-only">Acciones</span></th>
              </tr>
            </thead>
            <tbody>
              {usuarios.datos.map((u) => (
                <tr key={u.id_usuario}>
                  <td>
                    {u.nombres}
                    <span className="celda-secundaria">{u.correo}</span>
                  </td>
                  <td>{u.codigo}</td>
                  <td>{u.identificacion}</td>
                  <td>
                    {u.rol === "docente" ? "Docente" : "Estudiante"}
                    {u.carrera && <span className="celda-secundaria">{u.carrera}</span>}
                  </td>
                  <td><EtiquetaEstado estado={u.estado} /></td>
                  <td>
                    <div className="acciones acciones--fin">
                      <Link className="btn btn--secundario btn--pequeno" to={`/prestamos?usuario=${u.id_usuario}`}>
                        Ver préstamos
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialogo abierto={registrando} titulo="Registrar usuario" onCerrar={() => setRegistrando(false)}>
        <FormUsuario
          onCancelar={() => setRegistrando(false)}
          onGuardado={(u) => {
            setAviso({ tipo: "exito", texto: `${u.nombres} quedó registrado. Ya puede iniciar sesión con ${u.correo}.` });
            setRegistrando(false);
            usuarios.recargar();
          }}
        />
      </Dialogo>
    </>
  );
}
