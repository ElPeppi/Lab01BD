import { useMemo, useState } from "react";
import { devolucionesApi, multasApi } from "../../api/devoluciones";
import { mensajeError } from "../../api/errores";
import type { Devolucion } from "../../api/tipos";
import { useAuth } from "../../auth/AuthContext";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EtiquetaEstado } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { formatearFecha, formatearPesos, plural } from "../../utils/formato";

type Vista = "pendientes" | "pagadas" | "todas";
type ConMulta = Devolucion & { multa: NonNullable<Devolucion["multa"]> };

// Las devoluciones con multa traen todo lo que la tabla necesita (libro, días de retraso, monto)
const devolucionesConMulta = () => devolucionesApi.listar({ conMulta: true });

/** Personal: cobrar multas. Usuario: ver las suyas (el backend solo le devuelve las propias). */
export default function Multas() {
  const { perfil } = useAuth();
  const esEmpleado = perfil?.tipo === "empleado";
  const datos = useConsulta(devolucionesConMulta);
  const [vista, setVista] = useState<Vista>("pendientes");
  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [cobrando, setCobrando] = useState<ConMulta | null>(null);
  const [enviando, setEnviando] = useState(false);

  const todas = useMemo(() => (datos.datos ?? []).filter((d): d is ConMulta => d.multa !== null), [datos.datos]);
  const lista = todas.filter((d) => (vista === "todas" ? true : vista === "pagadas" ? d.multa.pagada : !d.multa.pagada));
  const pendiente = todas.filter((d) => !d.multa.pagada).reduce((t, d) => t + Number(d.multa.monto), 0);

  async function registrarPago() {
    if (!cobrando) return;
    setEnviando(true);
    try {
      await multasApi.pagar(cobrando.multa.id_multa);
      setAviso({ tipo: "exito", texto: `Pago registrado: ${cobrando.usuario_nombres} pagó ${formatearPesos(cobrando.multa.monto)}.` });
      datos.recargar();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
    } finally {
      setCobrando(null);
      setEnviando(false);
    }
  }

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>{esEmpleado ? "Multas" : "Mis multas"}</h1>
          <p>
            {!datos.datos
              ? "Multas generadas por devoluciones con retraso."
              : pendiente > 0
                ? `${esEmpleado ? "Por cobrar" : "Debes"}: ${formatearPesos(pendiente)}.`
                : esEmpleado
                  ? "No hay multas por cobrar."
                  : "No tienes multas pendientes."}
          </p>
        </div>
      </header>

      <div className="segmentos" role="group" aria-label="Qué multas ver">
        {(["pendientes", "pagadas", "todas"] as Vista[]).map((v) => (
          <button key={v} type="button" aria-pressed={vista === v} onClick={() => setVista(v)}>
            {v === "pendientes" ? "Pendientes" : v === "pagadas" ? "Pagadas" : "Todas"}
          </button>
        ))}
      </div>

      <Aviso aviso={aviso} onCerrar={() => setAviso(null)} />
      {datos.error && <ErrorCarga mensaje={datos.error} onReintentar={datos.recargar} />}
      {!datos.datos && datos.cargando && <Cargando texto="Cargando multas…" />}

      {datos.datos && lista.length === 0 && (
        <Vacio titulo={vista === "pendientes" ? "No hay multas pendientes" : vista === "pagadas" ? "No hay multas pagadas" : "No hay multas"}>
          <p>Las multas se generan solas cuando un libro se devuelve después de su fecha de vencimiento.</p>
        </Vacio>
      )}

      {lista.length > 0 && (
        <div className="tabla-contenedor" aria-busy={datos.cargando}>
          <table className="tabla">
            <thead>
              <tr>
                {esEmpleado && <th scope="col">Usuario</th>}
                <th scope="col">Libro</th>
                <th scope="col">Devuelto</th>
                <th scope="col">Retraso</th>
                <th scope="col" className="num">Monto</th>
                <th scope="col">Estado</th>
                {esEmpleado && <th scope="col"><span className="sr-only">Acciones</span></th>}
              </tr>
            </thead>
            <tbody>
              {lista.map((d) => (
                <tr key={d.multa.id_multa}>
                  {esEmpleado && <td>{d.usuario_nombres}</td>}
                  <td>{d.libro_titulo}</td>
                  <td>{formatearFecha(d.fecha_devolucion)}</td>
                  <td>{plural(d.dias_retraso, "día")}</td>
                  <td className="num">{formatearPesos(d.multa.monto)}</td>
                  <td><EtiquetaEstado estado={d.multa.pagada ? "pagada" : "pendiente"} /></td>
                  {esEmpleado && (
                    <td>
                      <div className="acciones acciones--fin">
                        {!d.multa.pagada && (
                          <button type="button" className="btn btn--secundario btn--pequeno" onClick={() => setCobrando(d)}>
                            Registrar pago
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialogo abierto={cobrando !== null} titulo="Registrar pago" onCerrar={() => setCobrando(null)}>
        <div className="dialogo-cuerpo">
          <p>
            {cobrando?.usuario_nombres} paga <strong>{cobrando && formatearPesos(cobrando.multa.monto)}</strong> por devolver{" "}
            <em>{cobrando?.libro_titulo}</em> con {cobrando && plural(cobrando.dias_retraso, "día")} de retraso.
          </p>
        </div>
        <div className="dialogo-pie">
          <button type="button" className="btn btn--secundario" onClick={() => setCobrando(null)}>Cancelar</button>
          <button type="button" className="btn" disabled={enviando} onClick={registrarPago}>
            {enviando ? "Registrando…" : "Registrar pago"}
          </button>
        </div>
      </Dialogo>
    </>
  );
}
