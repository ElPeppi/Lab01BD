import { useCallback, useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { mensajeError } from "../../api/errores";
import { prestamosApi, type FiltrosPrestamos } from "../../api/prestamos";
import type { Prestamo } from "../../api/tipos";
import { usuariosApi } from "../../api/usuarios";
import { useAuth } from "../../auth/AuthContext";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EstadoPrestamo } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { formatearFecha, plural } from "../../utils/formato";

type Vista = "solicitudes" | "activos" | "vencidos" | "todos";

const VISTAS: { id: Vista; texto: string; filtro: FiltrosPrestamos; vacio: string }[] = [
  { id: "solicitudes", texto: "Por revisar", filtro: { estado: "solicitado" }, vacio: "No hay solicitudes por revisar." },
  { id: "activos", texto: "Prestados", filtro: { activos: true }, vacio: "No hay libros prestados en este momento." },
  { id: "vencidos", texto: "Vencidos", filtro: { vencidos: true }, vacio: "Ningún préstamo está vencido." },
  { id: "todos", texto: "Historial", filtro: {}, vacio: "Todavía no hay préstamos registrados." },
];

const todosLosUsuarios = () => usuariosApi.listar();

/** Vista del personal: revisar solicitudes, seguir los préstamos y ver el historial de una persona. */
export default function GestionPrestamos() {
  const { perfil } = useAuth();
  // ?usuario=ID abre directo el historial de esa persona (enlace desde Usuarios)
  const [params, setParams] = useSearchParams();
  const usuario = params.get("usuario") ?? "";
  const [vista, setVista] = useState<Vista>(usuario ? "todos" : "solicitudes");
  const actual = VISTAS.find((v) => v.id === vista)!;
  const usuarios = useConsulta(todosLosUsuarios);
  const persona = usuarios.datos?.find((u) => String(u.id_usuario) === usuario);

  const consulta = useCallback(
    () =>
      prestamosApi.listar({
        ...VISTAS.find((v) => v.id === vista)!.filtro,
        usuario: usuario ? Number(usuario) : undefined,
      }),
    [vista, usuario],
  );
  const prestamos = useConsulta(consulta);

  function cambiarUsuario(valor: string) {
    const siguiente = new URLSearchParams(params);
    if (valor) siguiente.set("usuario", valor);
    else siguiente.delete("usuario");
    setParams(siguiente, { replace: true });
  }

  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [aprobando, setAprobando] = useState<number | null>(null);
  const [rechazando, setRechazando] = useState<Prestamo | null>(null);
  const [motivo, setMotivo] = useState("");
  const [errorMotivo, setErrorMotivo] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function aprobar(p: Prestamo) {
    if (!perfil) return;
    setAprobando(p.id_prestamo);
    setAviso(null);
    try {
      const r = await prestamosApi.aprobar(p.id_prestamo);
      setAviso({
        tipo: "exito",
        texto: `Préstamo aprobado: entrega el ejemplar ${r.ejemplar_codigo} a ${r.usuario_nombres}. Vence el ${formatearFecha(r.fecha_vencimiento)}.`,
      });
      prestamos.recargar();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
      prestamos.recargar(); // pudo cambiar mientras tanto (p. ej. otro bibliotecario lo atendió)
    } finally {
      setAprobando(null);
    }
  }

  function abrirRechazo(p: Prestamo) {
    setMotivo("");
    setErrorMotivo("");
    setRechazando(p);
  }

  async function rechazar(e: FormEvent) {
    e.preventDefault();
    if (!perfil || !rechazando) return;
    if (!motivo.trim()) {
      setErrorMotivo("Escribe el motivo; el usuario lo verá en sus préstamos.");
      return;
    }
    setEnviando(true);
    try {
      await prestamosApi.rechazar(rechazando.id_prestamo, motivo.trim());
      setAviso({ tipo: "exito", texto: `Se rechazó la solicitud de ${rechazando.usuario_nombres}.` });
      setRechazando(null);
      prestamos.recargar();
    } catch (err) {
      setErrorMotivo(mensajeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Préstamos</h1>
          <p>
            {persona
              ? `Préstamos de ${persona.nombres} (código ${persona.codigo})${prestamos.datos ? `: ${plural(prestamos.datos.length, "registro")}` : ""}.`
              : "Revisa las solicitudes, sigue los libros prestados y consulta el historial de cada persona."}
          </p>
        </div>
      </header>

      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <div className="campo campo--ancho">
          <label htmlFor="filtro-usuario">Usuario</label>
          <select id="filtro-usuario" value={usuario} onChange={(e) => cambiarUsuario(e.target.value)}>
            <option value="">Todos los usuarios</option>
            {usuarios.datos?.map((u) => (
              <option key={u.id_usuario} value={u.id_usuario}>
                {u.nombres} ({u.codigo})
              </option>
            ))}
          </select>
        </div>
      </form>

      <div className="segmentos" role="group" aria-label="Qué préstamos ver">
        {VISTAS.map((v) => (
          <button key={v.id} type="button" aria-pressed={vista === v.id} onClick={() => setVista(v.id)}>
            {v.texto}
          </button>
        ))}
      </div>

      <Aviso aviso={aviso} onCerrar={() => setAviso(null)} />
      {prestamos.error && <ErrorCarga mensaje={prestamos.error} onReintentar={prestamos.recargar} />}
      {!prestamos.datos && prestamos.cargando && <Cargando texto="Cargando préstamos…" />}

      {prestamos.datos && prestamos.datos.length === 0 && (
        <Vacio titulo={persona ? `${persona.nombres} no tiene préstamos en esta vista.` : actual.vacio} />
      )}

      {prestamos.datos && prestamos.datos.length > 0 && (
        <div className="tabla-contenedor" aria-busy={prestamos.cargando}>
          <table className="tabla">
            <thead>
              <tr>
                <th scope="col">Usuario</th>
                <th scope="col">Libro</th>
                <th scope="col">Solicitado</th>
                <th scope="col">Vence</th>
                <th scope="col">Estado</th>
                {vista === "solicitudes" && <th scope="col"><span className="sr-only">Acciones</span></th>}
              </tr>
            </thead>
            <tbody>
              {prestamos.datos.map((p) => (
                <tr key={p.id_prestamo}>
                  <td>
                    {p.usuario_nombres}
                    <span className="celda-secundaria">Código {p.usuario_codigo}</span>
                  </td>
                  <td>
                    {p.libro_titulo}
                    <span className="celda-secundaria">Ejemplar {p.ejemplar_codigo}</span>
                  </td>
                  <td>{formatearFecha(p.fecha_solicitud)}</td>
                  <td>{formatearFecha(p.fecha_vencimiento)}</td>
                  <td>
                    <EstadoPrestamo prestamo={p} />
                    {p.estado === "rechazado" && p.motivo_rechazo && <span className="celda-secundaria">{p.motivo_rechazo}</span>}
                  </td>
                  {vista === "solicitudes" && (
                    <td>
                      <div className="acciones acciones--fin">
                        <button type="button" className="btn btn--pequeno" disabled={aprobando !== null} onClick={() => aprobar(p)}>
                          {aprobando === p.id_prestamo ? "Aprobando…" : "Aprobar"}
                        </button>
                        <button type="button" className="btn btn--texto-peligro btn--pequeno" disabled={aprobando !== null} onClick={() => abrirRechazo(p)}>
                          Rechazar
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialogo abierto={rechazando !== null} titulo="Rechazar solicitud" onCerrar={() => setRechazando(null)}>
        <form onSubmit={rechazar} noValidate>
          <div className="dialogo-cuerpo">
            <p>
              {rechazando?.usuario_nombres} pidió <em>{rechazando?.libro_titulo}</em>.
            </p>
            <div className="campo">
              <label htmlFor="motivo">Motivo</label>
              <textarea
                id="motivo"
                rows={3}
                maxLength={255}
                value={motivo}
                onChange={(e) => setMotivo(e.target.value)}
                aria-invalid={Boolean(errorMotivo)}
                aria-describedby={errorMotivo ? "error-motivo" : undefined}
                autoFocus
              />
              {errorMotivo && <small className="error-campo" id="error-motivo">{errorMotivo}</small>}
            </div>
          </div>
          <div className="dialogo-pie">
            <button type="button" className="btn btn--secundario" onClick={() => setRechazando(null)}>Cancelar</button>
            <button type="submit" className="btn btn--peligro" disabled={enviando}>
              {enviando ? "Rechazando…" : "Rechazar solicitud"}
            </button>
          </div>
        </form>
      </Dialogo>
    </>
  );
}
