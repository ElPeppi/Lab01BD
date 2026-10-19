const fechaCorta = new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "short", year: "numeric" });

/**
 * Formatea "2026-10-25" o "2026-10-18T21:33:57-05:00".
 * Las fechas sin hora se arman en hora local: new Date("2026-10-25") las tomaría
 * como UTC y en Colombia (UTC-5) mostraría el día anterior.
 */
export function formatearFecha(valor: string | null | undefined): string {
  if (!valor) return "—";
  const soloFecha = /^(\d{4})-(\d{2})-(\d{2})$/.exec(valor);
  const fecha = soloFecha
    ? new Date(Number(soloFecha[1]), Number(soloFecha[2]) - 1, Number(soloFecha[3]))
    : new Date(valor);
  return Number.isNaN(fecha.getTime()) ? "—" : fechaCorta.format(fecha).replace(".", "");
}

const pesos = new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });

/** "4000.00" -> "$ 4.000" */
export function formatearPesos(valor: string | number): string {
  const n = Number(valor);
  return Number.isFinite(n) ? pesos.format(n) : "—";
}

export function plural(n: number, singular: string, pluralTexto = `${singular}s`) {
  return `${n} ${n === 1 ? singular : pluralTexto}`;
}

export const NOMBRE_ESTADO: Record<string, string> = {
  disponible: "Disponible",
  prestado: "Prestado",
  perdido: "Perdido",
  solicitado: "Solicitado",
  aprobado: "Aprobado",
  rechazado: "Rechazado",
  devuelto: "Devuelto",
  vencido: "Vencido",
  bueno: "Bueno",
  danado: "Dañado",
  pagada: "Pagada",
  pendiente: "Pendiente",
  activo: "Activo",
  bloqueado: "Bloqueado",
};
