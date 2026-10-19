import api from "./client";
import type { Autor, Categoria, Editorial, Libro, LibroEntrada } from "./tipos";

export type FiltrosLibros = {
  titulo?: string;
  autor?: string;
  categoria?: number;
  soloDisponibles?: boolean;
};

export const catalogoApi = {
  libros: (f: FiltrosLibros = {}) =>
    api
      .get<Libro[]>("/api/catalogo/libros/", {
        params: {
          titulo: f.titulo || undefined,
          autor: f.autor || undefined,
          categoria: f.categoria || undefined,
          disponible: f.soloDisponibles ? "true" : undefined,
        },
      })
      .then((r) => r.data),

  crearLibro: (datos: LibroEntrada) =>
    api.post<Libro>("/api/catalogo/libros/", datos).then((r) => r.data),

  actualizarLibro: (id: number, datos: LibroEntrada) =>
    api.put<Libro>(`/api/catalogo/libros/${id}/`, datos).then((r) => r.data),

  // Borrado lógico: el libro se oculta, su historial se conserva
  retirarLibro: (id: number) => api.delete(`/api/catalogo/libros/${id}/`),

  categorias: () => api.get<Categoria[]>("/api/catalogo/categorias/").then((r) => r.data),
  autores: () => api.get<Autor[]>("/api/catalogo/autores/").then((r) => r.data),
  editoriales: () => api.get<Editorial[]>("/api/catalogo/editoriales/").then((r) => r.data),
};
