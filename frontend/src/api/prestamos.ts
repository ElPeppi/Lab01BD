import api from "./client";
import type { EstadoPrestamo, Prestamo } from "./tipos";

export type FiltrosPrestamos = {
  estado?: EstadoPrestamo;
  usuario?: number;   // historial de una persona (personal). A un estudiante/docente el
                      // backend siempre le devuelve solo los suyos, por el token
  activos?: boolean;  // aprobados (sin devolver)
  vencidos?: boolean; // aprobados con fecha de vencimiento pasada
};

export const prestamosApi = {
  listar: (f: FiltrosPrestamos = {}) =>
    api
      .get<Prestamo[]>("/api/prestamos/", {
        params: {
          estado: f.estado || undefined,
          usuario: f.usuario || undefined,
          activos: f.activos ? "true" : undefined,
          vencidos: f.vencidos ? "true" : undefined,
        },
      })
      .then((r) => r.data),

  // Quién solicita y quién aprueba lo saca el backend del token: no se envía.
  // El backend elige el ejemplar libre del libro (en una transacción)
  solicitar: (libro: number) => api.post<Prestamo>("/api/prestamos/", { libro }).then((r) => r.data),

  // Sin fechas: se presta hoy y vence según la política del rol
  aprobar: (id: number) => api.post<Prestamo>(`/api/prestamos/${id}/aprobar/`, {}).then((r) => r.data),

  rechazar: (id: number, motivo_rechazo: string) =>
    api.post<Prestamo>(`/api/prestamos/${id}/rechazar/`, { motivo_rechazo }).then((r) => r.data),
};
