import { useCallback, useMemo, useState, type FormEvent } from "react";
import { devolucionesApi } from "../../api/devoluciones";
import { mensajeError } from "../../api/errores";
import { prestamosApi } from "../../api/prestamos";
import type { CondicionEjemplar, Prestamo } from "../../api/tipos";
import { useAuth } from "../../auth/AuthContext";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EstadoPrestamo } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { useDebounce } from "../../hooks/useDebounce";
import { formatearFecha, formatearPesos, plural } from "../../utils/formato";

const activos = () => prestamosApi.listar({ activos: true });

/** Libros que están fuera de la biblioteca, ordenados por cuál vence primero. */
export default function Devoluciones() {
  const { perfil } = useAuth();
  const prestamos = useConsulta(activos);
  const [texto, setTexto] = useState("");
  const busqueda = useDebounce(texto.trim().toLowerCase(), 200);

  const lista = useMemo(() => {
    const todos = [...(prestamos.datos ?? [])].sort((a, b) =>
      (a.fecha_vencimiento ?? "").localeCompare(b.fecha_vencimiento ?? ""),
    );
    if (!busqueda) return todos;
    return todos.filter((p) =>
      [p.usuario_nombres, p.usuario_codigo, p.libro_titulo, p.ejemplar_codigo].some((c) => c.toLowerCase().includes(busqueda)),
    );
  }, [prestamos.datos, busqueda]);

  const vencidos = prestamos.datos?.filter((p) => p.vencido).length ?? 0;

  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [devolviendo, setDevolviendo] = useState<Prestamo | null>(null);
  const [observaciones, setObservaciones] = useState("");
  const [condicion, setCondicion] = useState<CondicionEjemplar>("bueno");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  const abrir = useCallback((p: Prestamo) => {
    setObservaciones("");
    setCondicion("bueno");
    setError("");
    setDevolviendo(p);
  }, []);

  async function registrar(e: FormEvent) {
    e.preventDefault();
    if (!perfil || !devolviendo) return;
    setEnviando(true);
    setError("");
    try {
      const r = await devolucionesApi.registrar(devolviendo.id_prestamo, observaciones.trim(), condicion);
      const multa = r.multa
        ? ` Se generó una multa de ${formatearPesos(r.multa.monto)} por ${plural(r.dias_retraso, "día")} de retraso.`
        : " Llegó a tiempo: no hay multa.";
      setAviso({ tipo: "exito", texto: `Devolución registrada: ${devolviendo.ejemplar_codigo} vuelve a estar disponible.${multa}` });
      setDevolviendo(null);
      prestamos.recargar();
    } catch (err) {
      setError(mensajeError(err));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Devoluciones</h1>
          <p>
            {prestamos.datos
              ? `${plural(prestamos.datos.length, "libro")} por devolver${vencidos ? `, ${vencidos} ${vencidos === 1 ? "vencido" : "vencidos"}` : ""}.`
              : "Libros prestados pendientes de devolución."}
          </p>
        </div>
      </header>

      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <div className="campo campo--ancho">
          <label htmlFor="dev-buscar">Buscar</label>
          <input id="dev-buscar" type="search" value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Usuario, código, libro o ejemplar" />
        </div>
      </form>

      <Aviso aviso={aviso} onCerrar={() => setAviso(null)} />
      {prestamos.error && <ErrorCarga mensaje={prestamos.error} onReintentar={prestamos.recargar} />}
      {!prestamos.datos && prestamos.cargando && <Cargando texto="Cargando préstamos activos…" />}

      {prestamos.datos && lista.length === 0 && (
        <Vacio titulo={busqueda ? "Nada coincide con la búsqueda" : "No hay libros por devolver"} />
      )}

      {lista.length > 0 && (
        <div className="tabla-contenedor" aria-busy={prestamos.cargando}>
          <table className="tabla">
            <thead>
              <tr>
                <th scope="col">Usuario</th>
                <th scope="col">Libro</th>
                <th scope="col">Prestado</th>
                <th scope="col">Vence</th>
                <th scope="col">Estado</th>
                <th scope="col"><span className="sr-only">Acciones</span></th>
              </tr>
            </thead>
            <tbody>
              {lista.map((p) => (
                <tr key={p.id_prestamo} className={p.vencido ? "fila--aviso" : undefined}>
                  <td>
                    {p.usuario_nombres}
                    <span className="celda-secundaria">Código {p.usuario_codigo}</span>
                  </td>
                  <td>
                    {p.libro_titulo}
                    <span className="celda-secundaria">Ejemplar {p.ejemplar_codigo}</span>
                  </td>
                  <td>{formatearFecha(p.fecha_prestamo)}</td>
                  <td>{formatearFecha(p.fecha_vencimiento)}</td>
                  <td><EstadoPrestamo prestamo={p} /></td>
                  <td>
                    <div className="acciones acciones--fin">
                      <button type="button" className="btn btn--secundario btn--pequeno" onClick={() => abrir(p)}>
                        Registrar devolución
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialogo abierto={devolviendo !== null} titulo="Registrar devolución" onCerrar={() => setDevolviendo(null)}>
        <form onSubmit={registrar} noValidate>
          <div className="dialogo-cuerpo">
            {error && <div className="alerta alerta--error" role="alert">{error}</div>}
            <p>
              <strong>{devolviendo?.libro_titulo}</strong>, ejemplar {devolviendo?.ejemplar_codigo}, prestado a {devolviendo?.usuario_nombres}.
            </p>
            {devolviendo?.vencido && (
              <p className="alerta alerta--aviso">
                Se devuelve con {plural(devolviendo.dias_retraso, "día")} de retraso: se generará una multa.
              </p>
            )}
            <div className="campo">
              <label htmlFor="condicion">¿En qué condición vuelve?</label>
              <select id="condicion" value={condicion} onChange={(e) => setCondicion(e.target.value as CondicionEjemplar)}>
                <option value="bueno">Bueno</option>
                <option value="danado">Dañado</option>
              </select>
            </div>
            <div className="campo">
              <label htmlFor="observaciones">Observaciones (opcional)</label>
              <textarea id="observaciones" rows={3} maxLength={500} value={observaciones} onChange={(e) => setObservaciones(e.target.value)} placeholder="Ej. Llegó con la portada doblada" />
            </div>
          </div>
          <div className="dialogo-pie">
            <button type="button" className="btn btn--secundario" onClick={() => setDevolviendo(null)}>Cancelar</button>
            <button type="submit" className="btn" disabled={enviando}>{enviando ? "Registrando…" : "Registrar devolución"}</button>
          </div>
        </form>
      </Dialogo>
    </>
  );
}
