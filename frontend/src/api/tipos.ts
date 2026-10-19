// Tipos que reflejan exactamente lo que responde el backend (verificado contra la API).

export type Autor = { id_autor: number; nombre: string };
export type Categoria = { id_categoria: number; nombre: string };
export type Editorial = { id_editorial: number; nombre: string };

// GET /api/catalogo/libros/
export type Libro = {
  id_libro: number;
  isbn: string;
  titulo: string;
  anio: number;
  descripcion: string | null;
  editorial: number;
  editorial_nombre: string;
  categoria: number;
  categoria_nombre: string;
  autores_detalle: Autor[];
  // Solo vienen en el listado y el detalle (no en la respuesta de crear/editar)
  ejemplares_disponibles?: number;
  ejemplares_total?: number;
};

// POST/PUT /api/catalogo/libros/  (autores = lista de ids)
export type LibroEntrada = {
  isbn: string;
  titulo: string;
  anio: number;
  descripcion: string;
  editorial: number;
  categoria: number;
  autores: number[];
};

export type EstadoEjemplar = "disponible" | "prestado" | "perdido";
export type CondicionEjemplar = "bueno" | "danado";

// GET /api/ejemplares/
export type Ejemplar = {
  id_ejemplar: number;
  codigo_barras: string;
  ubicacion: string;
  estado: EstadoEjemplar;
  condicion: CondicionEjemplar;
  eliminado: boolean;
  id_libro: number;
  libro_titulo: string | null;
  libro_isbn: string | null;
};

export type EjemplarEntrada = {
  codigo_barras: string;
  id_libro: number;
  ubicacion: string;
  estado?: EstadoEjemplar;
  condicion: CondicionEjemplar;
};

// GET /api/ejemplares/inventario/?solo_resumen=true  -> resumen_global
export type ResumenInventario = {
  total: number;
  disponibles: number;
  prestados: number;
  perdidos: number;
  buenos: number;
  danados: number;
  pct_disponibles: number;
  pct_prestados: number;
  pct_perdidos: number;
};

export type EstadoPrestamo = "solicitado" | "aprobado" | "rechazado" | "devuelto";

// GET /api/prestamos/
export type Prestamo = {
  id_prestamo: number;
  estado: EstadoPrestamo;
  usuario: number;
  usuario_nombres: string;
  usuario_codigo: string;
  ejemplar: number;
  ejemplar_codigo: string;
  libro: number;
  libro_titulo: string;
  empleado: number | null;
  empleado_nombres: string | null;
  fecha_solicitud: string;        // datetime ISO con zona
  fecha_aprobacion: string | null; // datetime ISO con zona
  fecha_prestamo: string | null;   // fecha YYYY-MM-DD
  fecha_vencimiento: string | null; // fecha YYYY-MM-DD
  motivo_rechazo: string | null;
  vencido: boolean;
  dias_retraso: number;
};
