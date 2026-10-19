import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { mensajeError } from "../../api/errores";
import { usuariosApi, type Usuario } from "../../api/usuarios";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EtiquetaEstado } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { useDebounce } from "../../hooks/useDebounce";
import { plural } from "../../utils/formato";
import FormUsuario from "./FormUsuario";

/** Solo el administrador: registra, edita, bloquea y elimina estudiantes y docentes, y abre el historial de cada uno. */
export default function Usuarios() {
  const [texto, setTexto] = useState("");
  const q = useDebounce(texto.trim(), 300);
  const consulta = useCallback(() => usuariosApi.listar(q), [q]);
  const usuarios = useConsulta(consulta);

  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [editando, setEditando] = useState<Usuario | "nuevo" | null>(null);
  const [eliminando, setEliminando] = useState<Usuario | null>(null);
  const [cambiandoEstado, setCambiandoEstado] = useState<number | null>(null);
  const [procesando, setProcesando] = useState(false);

  async function alternarBloqueo(u: Usuario) {
    const bloquear = u.estado === "activo";
    setCambiandoEstado(u.id_usuario);
    setAviso(null);
    try {
      await usuariosApi.cambiarEstado(u.id_usuario, bloquear ? "bloqueado" : "activo");
      setAviso({
        tipo: "exito",
        texto: bloquear
          ? `Se bloqueó a ${u.nombres}: no podrá iniciar sesión ni pedir préstamos.`
          : `Se desbloqueó a ${u.nombres}: ya puede iniciar sesión y pedir préstamos.`,
      });
      usuarios.recargar();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
    } finally {
      setCambiandoEstado(null);
    }
  }

  async function confirmarEliminacion() {
    if (!eliminando) return;
    setProcesando(true);
    try {
      await usuariosApi.eliminar(eliminando.id_usuario);
      setAviso({ tipo: "exito", texto: `Se eliminó a ${eliminando.nombres}.` });
      usuarios.recargar();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
    } finally {
      setEliminando(null);
      setProcesando(false);
    }
  }

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
        <button type="button" className="btn" onClick={() => setEditando("nuevo")}>
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
                  <td>
                    {u.codigo}
                    <span className="celda-secundaria">Doc. {u.identificacion}</span>
                  </td>
                  <td>
                    {u.rol === "docente" ? "Docente" : "Estudiante"}
                    {u.carrera && <span className="celda-secundaria">{u.carrera}</span>}
                  </td>
                  <td><EtiquetaEstado estado={u.estado} /></td>
                  <td>
                    <div className="acciones--rejilla">
                      <Link className="btn btn--secundario btn--pequeno" to={`/prestamos?usuario=${u.id_usuario}`}>
                        Ver préstamos
                      </Link>
                      <button type="button" className="btn btn--texto btn--pequeno" onClick={() => setEditando(u)}>
                        Editar
                      </button>
                      <button
                        type="button"
                        className={`btn btn--pequeno ${u.estado === "activo" ? "btn--texto-peligro" : "btn--texto"}`}
                        disabled={cambiandoEstado !== null}
                        onClick={() => alternarBloqueo(u)}
                      >
                        {cambiandoEstado === u.id_usuario ? "Guardando…" : u.estado === "activo" ? "Bloquear" : "Desbloquear"}
                      </button>
                      <button type="button" className="btn btn--texto-peligro btn--pequeno" onClick={() => setEliminando(u)}>
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialogo
        abierto={editando !== null}
        titulo={editando === "nuevo" ? "Registrar usuario" : "Editar usuario"}
        onCerrar={() => setEditando(null)}
      >
        <FormUsuario
          usuario={editando === "nuevo" ? null : editando}
          onCancelar={() => setEditando(null)}
          onGuardado={(u) => {
            setAviso({
              tipo: "exito",
              texto: editando === "nuevo"
                ? `${u.nombres} quedó registrado. Ya puede iniciar sesión con ${u.correo}.`
                : `Se guardaron los cambios de ${u.nombres}.`,
            });
            setEditando(null);
            usuarios.recargar();
          }}
        />
      </Dialogo>

      <Dialogo abierto={eliminando !== null} titulo="Eliminar usuario" onCerrar={() => setEliminando(null)}>
        <div className="dialogo-cuerpo">
          <p>
            <strong>{eliminando?.nombres}</strong> dejará de aparecer en la lista y no podrá iniciar sesión. Su historial de
            préstamos se conserva.
          </p>
          <p className="texto-suave">No se puede eliminar a quien tenga préstamos en curso o multas sin pagar.</p>
        </div>
        <div className="dialogo-pie">
          <button type="button" className="btn btn--secundario" onClick={() => setEliminando(null)}>Cancelar</button>
          <button type="button" className="btn btn--peligro" disabled={procesando} onClick={confirmarEliminacion}>
            {procesando ? "Eliminando…" : "Eliminar usuario"}
          </button>
        </div>
      </Dialogo>
    </>
  );
}
