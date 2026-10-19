import { useCallback } from "react";
import { Link } from "react-router-dom";
import { prestamosApi } from "../../api/prestamos";
import { useAuth } from "../../auth/AuthContext";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EstadoPrestamo } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { formatearFecha } from "../../utils/formato";

/** Vista del estudiante o docente: solo sus préstamos. */
export default function MisPrestamos() {
  const { perfil } = useAuth();
  const consulta = useCallback(() => prestamosApi.listar({ usuario: perfil?.id }), [perfil?.id]);
  const prestamos = useConsulta(consulta);

  const abiertos = prestamos.datos?.filter((p) => p.estado === "solicitado" || p.estado === "aprobado").length ?? 0;
  const vencidos = prestamos.datos?.filter((p) => p.vencido) ?? [];

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Mis préstamos</h1>
          <p>
            {prestamos.datos
              ? `Tienes ${abiertos} ${abiertos === 1 ? "préstamo abierto" : "préstamos abiertos"} entre solicitudes y libros en tu poder.`
              : "Tus solicitudes y los libros que tienes prestados."}
          </p>
        </div>
        <Link className="btn btn--secundario" to="/catalogo">Buscar un libro</Link>
      </header>

      {vencidos.length > 0 && (
        <div className="alerta alerta--aviso" role="status">
          {vencidos.length === 1
            ? `"${vencidos[0].libro_titulo}" está vencido. Devuélvelo pronto: la multa aumenta cada día.`
            : `Tienes ${vencidos.length} libros vencidos. Devuélvelos pronto: la multa aumenta cada día.`}
        </div>
      )}

      {prestamos.error && <ErrorCarga mensaje={prestamos.error} onReintentar={prestamos.recargar} />}
      {!prestamos.datos && prestamos.cargando && <Cargando texto="Cargando tus préstamos…" />}

      {prestamos.datos && prestamos.datos.length === 0 && (
        <Vacio titulo="Aún no tienes préstamos">
          <p>Busca un libro en el catálogo y solicítalo; aquí verás cuándo lo aprueben.</p>
          <Link className="btn" to="/catalogo">Ir al catálogo</Link>
        </Vacio>
      )}

      {prestamos.datos && prestamos.datos.length > 0 && (
        <div className="tabla-contenedor">
          <table className="tabla">
            <thead>
              <tr>
                <th scope="col">Libro</th>
                <th scope="col">Solicitado</th>
                <th scope="col">Prestado</th>
                <th scope="col">Vence</th>
                <th scope="col">Estado</th>
              </tr>
            </thead>
            <tbody>
              {prestamos.datos.map((p) => (
                <tr key={p.id_prestamo}>
                  <td>
                    {p.libro_titulo}
                    <span className="celda-secundaria">Ejemplar {p.ejemplar_codigo}</span>
                  </td>
                  <td>{formatearFecha(p.fecha_solicitud)}</td>
                  <td>{formatearFecha(p.fecha_prestamo)}</td>
                  <td>{formatearFecha(p.fecha_vencimiento)}</td>
                  <td>
                    <EstadoPrestamo prestamo={p} />
                    {p.estado === "rechazado" && p.motivo_rechazo && (
                      <span className="celda-secundaria">{p.motivo_rechazo}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
