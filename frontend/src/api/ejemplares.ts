import api from "./client";
import type { Ejemplar, EjemplarEntrada, EstadoEjemplar, ResumenInventario } from "./tipos";

export type FiltrosEjemplares = { q?: string; estado?: EstadoEjemplar; libro?: number };

export const ejemplaresApi = {
  listar: (f: FiltrosEjemplares = {}) =>
    api
      .get<{ count: number; results: Ejemplar[] }>("/api/ejemplares/", {
        params: { q: f.q || undefined, estado: f.estado || undefined, id_libro: f.libro || undefined },
      })
      .then((r) => r.data.results),

  crear: (datos: EjemplarEntrada) => api.post<Ejemplar>("/api/ejemplares/", datos).then((r) => r.data),

  actualizar: (id: number, datos: Partial<EjemplarEntrada>) =>
    api.patch<Ejemplar>(`/api/ejemplares/${id}/`, datos).then((r) => r.data),

  // Borrado lógico (el backend lo rechaza si está prestado o tiene una solicitud pendiente)
  darDeBaja: (id: number) => api.delete(`/api/ejemplares/${id}/`),

  resumenInventario: () =>
    api
      .get<{ resumen_global: ResumenInventario }>("/api/ejemplares/inventario/", {
        params: { solo_resumen: "true" }, // solo los totales, sin la lista de 90+ ejemplares
      })
      .then((r) => r.data.resumen_global),
};
