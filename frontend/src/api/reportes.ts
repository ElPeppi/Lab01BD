import api from "./client";

export type ResumenKPIs = {
  libros: { total: number };
  ejemplares: {
    total: number;
    disponibles: number;
    prestados: number;
    perdidos: number;
    danados: number;
  };
  prestamos: {
    total: number;
    solicitados: number;
    aprobados: number;
    devueltos: number;
    rechazados: number;
    vencidos: number;
  };
  multas: {
    total: number;
    pagadas: number;
    pendientes: number;
    monto_total: string;
    monto_pagado: string;
    monto_pendiente: string;
  };
  usuarios: {
    total: number;
    activos: number;
    bloqueados: number;
  };
};

export type LibroPopular = {
  id_libro: number;
  isbn: string;
  titulo: string;
  anio: number;
  categoria: string | null;
  editorial: string | null;
  total_prestamos: number;
  prestamos_activos: number;
  ejemplares_disponibles: number;
  ejemplares_totales: number;
};

export type MorosoItem = {
  id_prestamo: number;
  usuario: {
    id_usuario: number;
    codigo: string;
    identificacion: string;
    nombres: string;
    correo: string;
    carrera: string | null;
    rol: string;
  };
  ejemplar: {
    id_ejemplar: number;
    codigo_barras: string;
    ubicacion: string;
    libro_titulo: string;
    libro_isbn: string;
  };
  fecha_prestamo: string;
  fecha_vencimiento: string;
  dias_retraso: number;
  tarifa_dia: string;
  multa_estimada: string;
};

export type ReporteMorosos = {
  total_morosos: number;
  tarifa_dia: string;
  total_multa_estimada: string;
  morosos: MorosoItem[];
};

export type ReportePrestamosPeriodo = {
  total: number;
  conteo_estados: {
    solicitado: number;
    aprobado: number;
    devuelto: number;
    rechazado: number;
  };
  prestamos: Array<{
    id_prestamo: number;
    estado: string;
    usuario_codigo: string;
    usuario_nombres: string;
    libro_titulo: string;
    ejemplar_codigo: string;
    fecha_solicitud: string | null;
    fecha_prestamo: string | null;
    fecha_vencimiento: string | null;
    vencido: boolean;
    dias_retraso: number;
  }>;
};

export type ReporteMultasRecaudo = {
  resumen: {
    total_multas: number;
    pagadas_count: number;
    pendientes_count: number;
    monto_total: string;
    monto_pagado: string;
    monto_pendiente: string;
  };
  multas: Array<{
    id_multa: number;
    monto: string;
    pagada: boolean;
    fecha_pago: string | null;
    fecha_devolucion: string | null;
    usuario_codigo: string;
    usuario_nombres: string;
    libro_titulo: string;
  }>;
};

export type UsuarioActividad = {
  id_usuario: number;
  codigo: string;
  nombres: string;
  correo: string;
  carrera: string | null;
  rol: string;
  estado: string;
  total_prestamos: number;
  prestamos_activos: number;
  prestamos_devueltos: number;
  multas_count: number;
  multas_pendientes: number;
  total_monto_multas: string;
};

export const reportesApi = {
  resumen: () => api.get<ResumenKPIs>("/api/reportes/resumen/").then((r) => r.data),

  librosPopulares: (params?: { desde?: string; hasta?: string; categoria?: number; limit?: number }) =>
    api.get<LibroPopular[]>("/api/reportes/libros-populares/", { params }).then((r) => r.data),

  morosos: (params?: { carrera?: string; dias_minimos?: number }) =>
    api.get<ReporteMorosos>("/api/reportes/morosos/", { params }).then((r) => r.data),

  prestamosPeriodo: (params?: { desde?: string; hasta?: string; estado?: string }) =>
    api.get<ReportePrestamosPeriodo>("/api/reportes/prestamos-periodo/", { params }).then((r) => r.data),

  multasRecaudo: (params?: { desde?: string; hasta?: string; pagada?: boolean }) =>
    api
      .get<ReporteMultasRecaudo>("/api/reportes/multas-recaudo/", {
        params: {
          ...params,
          pagada: params?.pagada !== undefined ? String(params.pagada) : undefined,
        },
      })
      .then((r) => r.data),

  usuariosActividad: (params?: { rol?: string; carrera?: string; limit?: number }) =>
    api.get<UsuarioActividad[]>("/api/reportes/usuarios-actividad/", { params }).then((r) => r.data),

  descargarCSV: async (tipo: "libros-populares" | "morosos" | "multas") => {
    const res = await api.get(`/api/reportes/exportar/?tipo=${tipo}`, {
      responseType: "blob",
    });
    const blob = new Blob([res.data], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `reporte_${tipo}_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
};
