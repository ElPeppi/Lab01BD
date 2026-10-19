import type { Prestamo } from "../api/tipos";
import { NOMBRE_ESTADO, plural } from "../utils/formato";

/** Etiqueta de color para cualquier estado de la BD (usa las clases .estado--*). */
export function EtiquetaEstado({ estado }: { estado: string }) {
  return <span className={`estado estado--${estado}`}>{NOMBRE_ESTADO[estado] ?? estado}</span>;
}

/** Para préstamos: un aprobado con fecha pasada se muestra como vencido (dato calculado por el backend). */
export function EstadoPrestamo({ prestamo }: { prestamo: Pick<Prestamo, "estado" | "vencido" | "dias_retraso"> }) {
  if (prestamo.vencido) {
    return (
      <span className="estado estado--vencido">
        Vencido, {plural(prestamo.dias_retraso, "día")}
      </span>
    );
  }
  return <EtiquetaEstado estado={prestamo.estado} />;
}
