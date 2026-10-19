import api from "./client";
import type { CondicionEjemplar, Devolucion, Multa } from "./tipos";

// Módulo de devoluciones (backend/devoluciones). El empleado sale del token.
// Al registrar, en una transacción: crea la devolución, pasa el préstamo a "devuelto",
// el ejemplar a "disponible" con la condición indicada y, si hubo retraso, crea la multa
// (días de retraso × tarifa_multa_dia de la tabla configuracion).

export const devolucionesApi = {
  registrar: (prestamo: number, observaciones: string, condicion: CondicionEjemplar) =>
    api
      .post<Devolucion>("/api/devoluciones/", {
        prestamo,
        condicion,
        observaciones: observaciones || undefined,
      })
      .then((r) => r.data),

  // con_multa=true: solo las devoluciones que generaron multa (trae libro y días de retraso)
  listar: (f: { conMulta?: boolean } = {}) =>
    api
      .get<Devolucion[]>("/api/devoluciones/", { params: { con_multa: f.conMulta ? "true" : undefined } })
      .then((r) => r.data),
};

export const multasApi = {
  listar: (f: { pagada?: boolean } = {}) =>
    api
      .get<Multa[]>("/api/multas/", { params: { pagada: f.pagada === undefined ? undefined : String(f.pagada) } })
      .then((r) => r.data),

  pagar: (id: number) => api.post<Multa>(`/api/multas/${id}/pagar/`).then((r) => r.data),
};
