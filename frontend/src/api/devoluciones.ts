import api from "./client";

// ⚠️ El módulo de devoluciones del backend todavía no existe.
// Contrato propuesto para quien lo implemente (mismo estilo que préstamos):
//   POST /api/devoluciones/   { prestamo: id, observaciones?: string }   (el empleado sale del token)
//   -> 201 { id_devolucion, prestamo, fecha_devolucion, dias_retraso, multa: { monto, pagada } | null }
// En una transacción: crea la devolución, pasa el préstamo a "devuelto", el ejemplar a
// "disponible" y, si hubo retraso, crea la multa (días de retraso × tarifa_multa_dia).

export type RespuestaDevolucion = {
  id_devolucion: number;
  prestamo: number;
  fecha_devolucion: string;
  dias_retraso?: number;
  multa?: { monto: string | number; pagada: boolean } | null;
};

export const devolucionesApi = {
  registrar: (prestamo: number, observaciones: string) =>
    api
      .post<RespuestaDevolucion>("/api/devoluciones/", {
        prestamo,
        observaciones: observaciones || undefined,
      })
      .then((r) => r.data),
};
