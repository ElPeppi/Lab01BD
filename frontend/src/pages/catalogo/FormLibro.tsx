import { useMemo, useState, type FormEvent } from "react";
import { catalogoApi } from "../../api/catalogo";
import { erroresDeCampo, mensajeError } from "../../api/errores";
import type { Libro, LibroEntrada } from "../../api/tipos";
import { useConsulta } from "../../hooks/useConsulta";

type Props = { libro: Libro | null; onGuardado: (l: Libro) => void; onCancelar: () => void };

/** Crear o editar un libro. Va dentro de <Dialogo>. */
export default function FormLibro({ libro, onGuardado, onCancelar }: Props) {
  const editoriales = useConsulta(catalogoApi.editoriales);
  const categorias = useConsulta(catalogoApi.categorias);
  const autores = useConsulta(catalogoApi.autores);

  const [datos, setDatos] = useState({
    isbn: libro?.isbn ?? "",
    titulo: libro?.titulo ?? "",
    anio: libro ? String(libro.anio) : "",
    descripcion: libro?.descripcion ?? "",
    editorial: libro ? String(libro.editorial) : "",
    categoria: libro ? String(libro.categoria) : "",
  });
  const [seleccion, setSeleccion] = useState<Set<number>>(
    () => new Set(libro?.autores_detalle.map((a) => a.id_autor) ?? []),
  );
  const [filtroAutor, setFiltroAutor] = useState("");
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [guardando, setGuardando] = useState(false);

  const autoresVisibles = useMemo(() => {
    const f = filtroAutor.trim().toLowerCase();
    return (autores.datos ?? []).filter((a) => !f || a.nombre.toLowerCase().includes(f) || seleccion.has(a.id_autor));
  }, [autores.datos, filtroAutor, seleccion]);

  const cambiar = (campo: keyof typeof datos) => (e: { target: { value: string } }) =>
    setDatos((d) => ({ ...d, [campo]: e.target.value }));

  function alternarAutor(id: number) {
    setSeleccion((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });
  }

  // Lo que el front puede validar solo, con mensajes claros; lo demás lo valida el backend
  function validar() {
    const e: Record<string, string> = {};
    if (!datos.titulo.trim()) e.titulo = "Escribe el título.";
    if (!datos.isbn.trim()) e.isbn = "Escribe el ISBN.";
    if (!datos.anio) e.anio = "Escribe el año de publicación.";
    if (!datos.editorial) e.editorial = "Elige la editorial.";
    if (!datos.categoria) e.categoria = "Elige la categoría.";
    if (seleccion.size === 0) e.autores = "Elige al menos un autor.";
    return e;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErrorGeneral("");
    const locales = validar();
    setErrores(locales);
    if (Object.keys(locales).length) return;
    const entrada: LibroEntrada = {
      isbn: datos.isbn.trim(),
      titulo: datos.titulo.trim(),
      anio: Number(datos.anio),
      descripcion: datos.descripcion.trim(),
      editorial: Number(datos.editorial),
      categoria: Number(datos.categoria),
      autores: [...seleccion],
    };
    setGuardando(true);
    try {
      const guardado = libro
        ? await catalogoApi.actualizarLibro(libro.id_libro, entrada)
        : await catalogoApi.crearLibro(entrada);
      onGuardado(guardado);
    } catch (err) {
      setErrores(erroresDeCampo(err));
      setErrorGeneral(mensajeError(err));
    } finally {
      setGuardando(false);
    }
  }

  const errorDe = (campo: string) =>
    errores[campo] ? (
      <small className="error-campo" id={`error-${campo}`}>
        {errores[campo]}
      </small>
    ) : null;
  const invalido = (campo: string) =>
    errores[campo] ? { "aria-invalid": true, "aria-describedby": `error-${campo}` } : {};

  return (
    <form onSubmit={onSubmit} noValidate>
      <div className="dialogo-cuerpo">
        {errorGeneral && <div className="alerta alerta--error" role="alert">{errorGeneral}</div>}

        <div className="campo">
          <label htmlFor="libro-titulo">Título</label>
          <input id="libro-titulo" value={datos.titulo} onChange={cambiar("titulo")} required maxLength={200} {...invalido("titulo")} />
          {errorDe("titulo")}
        </div>

        <div className="fila-campos">
          <div className="campo">
            <label htmlFor="libro-isbn">ISBN</label>
            <input id="libro-isbn" value={datos.isbn} onChange={cambiar("isbn")} required maxLength={17} {...invalido("isbn")} />
            {errorDe("isbn")}
          </div>
          <div className="campo campo--corto">
            <label htmlFor="libro-anio">Año</label>
            <input id="libro-anio" type="number" inputMode="numeric" min={1400} max={2100} value={datos.anio} onChange={cambiar("anio")} required {...invalido("anio")} />
            {errorDe("anio")}
          </div>
        </div>

        <div className="fila-campos">
          <div className="campo">
            <label htmlFor="libro-editorial">Editorial</label>
            <select id="libro-editorial" value={datos.editorial} onChange={cambiar("editorial")} required {...invalido("editorial")}>
              <option value="">Elige una editorial</option>
              {editoriales.datos?.map((ed) => (
                <option key={ed.id_editorial} value={ed.id_editorial}>{ed.nombre}</option>
              ))}
            </select>
            {errorDe("editorial")}
          </div>
          <div className="campo">
            <label htmlFor="libro-categoria">Categoría</label>
            <select id="libro-categoria" value={datos.categoria} onChange={cambiar("categoria")} required {...invalido("categoria")}>
              <option value="">Elige una categoría</option>
              {categorias.datos?.map((c) => (
                <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
              ))}
            </select>
            {errorDe("categoria")}
          </div>
        </div>

        <fieldset className="campo" aria-describedby={errores.autores ? "error-autores" : undefined}>
          <legend>Autores ({seleccion.size} elegidos)</legend>
          <input
            type="search"
            placeholder="Filtrar autores"
            aria-label="Filtrar autores"
            value={filtroAutor}
            onChange={(e) => setFiltroAutor(e.target.value)}
          />
          <div className="lista-casillas">
            {autores.cargando && !autores.datos && <span className="texto-suave">Cargando autores…</span>}
            {autoresVisibles.map((a) => (
              <label key={a.id_autor}>
                <input type="checkbox" checked={seleccion.has(a.id_autor)} onChange={() => alternarAutor(a.id_autor)} />
                {a.nombre}
              </label>
            ))}
          </div>
          {errorDe("autores")}
        </fieldset>

        <div className="campo">
          <label htmlFor="libro-descripcion">Descripción</label>
          <textarea id="libro-descripcion" rows={3} value={datos.descripcion} onChange={cambiar("descripcion")} />
          {errorDe("descripcion")}
        </div>
      </div>

      <div className="dialogo-pie">
        <button type="button" className="btn btn--secundario" onClick={onCancelar}>Cancelar</button>
        <button type="submit" className="btn" disabled={guardando}>
          {guardando ? "Guardando…" : libro ? "Guardar cambios" : "Agregar libro"}
        </button>
      </div>
    </form>
  );
}
