import { isAxiosError } from "axios";

// El backend responde los errores con formas distintas según el módulo:
//   DRF:        {"detail": "..."}  |  {"campo": ["..."]}  |  {"non_field_errors": ["..."]}
//   ejemplares: {"error": "..."}   |  {"errors": {"campo": ["..."]}}
// Estas funciones los convierten en texto para mostrar.

type Cuerpo = Record<string, unknown>;

function primerMensaje(valor: unknown): string | null {
  if (typeof valor === "string") return valor;
  if (Array.isArray(valor) && valor.length) return primerMensaje(valor[0]);
  return null;
}

/** Errores por campo, para marcar cada input del formulario. */
export function erroresDeCampo(err: unknown): Record<string, string> {
  if (!isAxiosError(err) || !err.response || typeof err.response.data !== "object") return {};
  const data = err.response.data as Cuerpo;
  const campos = (data.errors && typeof data.errors === "object" ? data.errors : data) as Cuerpo;
  const salida: Record<string, string> = {};
  for (const [campo, valor] of Object.entries(campos)) {
    if (campo === "detail" || campo === "error" || campo === "non_field_errors") continue;
    const msg = primerMensaje(valor);
    if (msg) salida[campo] = msg;
  }
  return salida;
}

/** Un solo mensaje legible para mostrar en una alerta. */
export function mensajeError(err: unknown, porDefecto = "No se pudo completar la acción. Intenta de nuevo."): string {
  if (!isAxiosError(err)) return porDefecto;
  if (!err.response) return "No hay conexión con el servidor. Revisa que el backend esté encendido.";

  const { status, data } = err.response;
  if (data && typeof data === "object") {
    const d = data as Cuerpo;
    const directo = primerMensaje(d.detail) ?? primerMensaje(d.error) ?? primerMensaje(d.non_field_errors);
    if (directo) return directo;
    const campos = Object.values(erroresDeCampo(err));
    if (campos.length) return "Revisa los campos marcados.";
  }
  if (status === 401) return "Tu sesión expiró. Vuelve a iniciar sesión.";
  if (status === 403) return "No tienes permiso para hacer esto.";
  if (status === 404) return "No se encontró lo que buscabas.";
  if (status >= 500) return "El servidor tuvo un error. Intenta de nuevo en un momento.";
  return porDefecto;
}

export function esNoEncontrado(err: unknown) {
  return isAxiosError(err) && err.response?.status === 404;
}
