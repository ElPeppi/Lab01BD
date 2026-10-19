import { useState, type FormEvent } from "react";
import { ejemplaresApi } from "../../api/ejemplares";
import { erroresDeCampo, mensajeError } from "../../api/errores";
import type { CondicionEjemplar, Ejemplar, EstadoEjemplar, Libro } from "../../api/tipos";

type Props = {
  ejemplar: Ejemplar | null;
  libros: Libro[];
  libroInicial?: number;
  onGuardado: (e: Ejemplar) => void;
  onCancelar: () => void;
};

export default function FormEjemplar({ ejemplar, libros, libroInicial, onGuardado, onCancelar }: Props) {
  const [codigo, setCodigo] = useState(ejemplar?.codigo_barras ?? "");
  const [libro, setLibro] = useState(String(ejemplar?.id_libro ?? libroInicial ?? ""));
  const [ubicacion, setUbicacion] = useState(ejemplar?.ubicacion ?? "");
  const [estado, setEstado] = useState<EstadoEjemplar>(ejemplar?.estado ?? "disponible");
  const [condicion, setCondicion] = useState<CondicionEjemplar>(ejemplar?.condicion ?? "bueno");
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [guardando, setGuardando] = useState(false);

  // "prestado" solo lo pone el flujo de préstamos; a mano solo se alterna disponible/perdido
  const prestado = ejemplar?.estado === "prestado";

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErrorGeneral("");
    const locales: Record<string, string> = {};
    if (!libro) locales.libro = "Elige el libro al que pertenece la copia.";
    if (!codigo.trim()) locales.codigo_barras = "Escribe el código de barras.";
    if (!ubicacion.trim()) locales.ubicacion = "Escribe dónde está (sala y estante).";
    setErrores(locales);
    if (Object.keys(locales).length) return;
    setGuardando(true);
    try {
      const datos = {
        codigo_barras: codigo.trim(),
        id_libro: Number(libro),
        ubicacion: ubicacion.trim(),
        condicion,
        ...(prestado ? {} : { estado }),
      };
      const guardado = ejemplar
        ? await ejemplaresApi.actualizar(ejemplar.id_ejemplar, datos)
        : await ejemplaresApi.crear(datos);
      onGuardado(guardado);
    } catch (err) {
      setErrores(erroresDeCampo(err)); // el backend responde el campo como "libro"

      setErrorGeneral(mensajeError(err));
    } finally {
      setGuardando(false);
    }
  }

  const error = (campo: string) =>
    errores[campo] ? <small className="error-campo" id={`err-ej-${campo}`}>{errores[campo]}</small> : null;
  const inv = (campo: string) =>
    errores[campo] ? { "aria-invalid": true, "aria-describedby": `err-ej-${campo}` } : {};

  return (
    <form onSubmit={onSubmit} noValidate>
      <div className="dialogo-cuerpo">
        {errorGeneral && <div className="alerta alerta--error" role="alert">{errorGeneral}</div>}

        <div className="campo">
          <label htmlFor="ej-libro">Libro</label>
          <select id="ej-libro" value={libro} onChange={(e) => setLibro(e.target.value)} required {...inv("libro")}>
            <option value="">Elige el libro</option>
            {libros.map((l) => (
              <option key={l.id_libro} value={l.id_libro}>{l.titulo}</option>
            ))}
          </select>
          {error("libro")}
        </div>

        <div className="fila-campos">
          <div className="campo">
            <label htmlFor="ej-codigo">Código de barras</label>
            <input id="ej-codigo" value={codigo} onChange={(e) => setCodigo(e.target.value)} maxLength={30} placeholder="Ej. BC-0094" required {...inv("codigo_barras")} />
            {error("codigo_barras")}
          </div>
          <div className="campo">
            <label htmlFor="ej-condicion">Condición</label>
            <select id="ej-condicion" value={condicion} onChange={(e) => setCondicion(e.target.value as CondicionEjemplar)}>
              <option value="bueno">Bueno</option>
              <option value="danado">Dañado</option>
            </select>
          </div>
        </div>

        <div className="campo">
          <label htmlFor="ej-ubicacion">Ubicación</label>
          <input id="ej-ubicacion" value={ubicacion} onChange={(e) => setUbicacion(e.target.value)} maxLength={60} placeholder="Ej. Sala General, estante A1" required {...inv("ubicacion")} />
          {error("ubicacion")}
        </div>

        {ejemplar && (
          <div className="campo">
            <label htmlFor="ej-estado">Estado</label>
            {prestado ? (
              <>
                <input id="ej-estado" value="Prestado" disabled />
                <small>Vuelve a quedar disponible cuando se registre la devolución.</small>
              </>
            ) : (
              <select id="ej-estado" value={estado} onChange={(e) => setEstado(e.target.value as EstadoEjemplar)}>
                <option value="disponible">Disponible</option>
                <option value="perdido">Perdido</option>
              </select>
            )}
          </div>
        )}
      </div>

      <div className="dialogo-pie">
        <button type="button" className="btn btn--secundario" onClick={onCancelar}>Cancelar</button>
        <button type="submit" className="btn" disabled={guardando}>
          {guardando ? "Guardando…" : ejemplar ? "Guardar cambios" : "Registrar ejemplar"}
        </button>
      </div>
    </form>
  );
}
