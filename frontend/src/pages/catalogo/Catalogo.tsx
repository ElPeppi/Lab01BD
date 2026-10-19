import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { catalogoApi } from "../../api/catalogo";
import { mensajeError } from "../../api/errores";
import { prestamosApi } from "../../api/prestamos";
import type { Libro } from "../../api/tipos";
import { useAuth } from "../../auth/AuthContext";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { useConsulta } from "../../hooks/useConsulta";
import { useDebounce } from "../../hooks/useDebounce";
import { plural } from "../../utils/formato";
import FormLibro from "./FormLibro";
import "./Catalogo.css";

type BuscarPor = "titulo" | "autor" | "isbn";

const BUSQUEDAS: Record<BuscarPor, { etiqueta: string; ejemplo: string }> = {
  titulo: { etiqueta: "Título", ejemplo: "Ej. Cien años de soledad" },
  autor: { etiqueta: "Autor", ejemplo: "Ej. García Márquez" },
  isbn: { etiqueta: "ISBN", ejemplo: "Ej. 978-0307474728" },
};

export default function Catalogo() {
  const { perfil } = useAuth();
  const esEmpleado = perfil?.tipo === "empleado";

  const [texto, setTexto] = useState("");
  const [buscarPor, setBuscarPor] = useState<BuscarPor>("titulo");
  const [categoria, setCategoria] = useState("");
  const [soloDisponibles, setSoloDisponibles] = useState(false);
  const busqueda = useDebounce(texto.trim(), 300);

  const consulta = useCallback(
    () =>
      catalogoApi.libros({
        [buscarPor]: busqueda,
        categoria: categoria ? Number(categoria) : undefined,
        soloDisponibles,
      }),
    [buscarPor, busqueda, categoria, soloDisponibles],
  );
  const libros = useConsulta(consulta);
  const categorias = useConsulta(catalogoApi.categorias);

  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [solicitando, setSolicitando] = useState<number | null>(null);
  const [editando, setEditando] = useState<Libro | "nuevo" | null>(null);
  const [retirando, setRetirando] = useState<Libro | null>(null);
  const [procesando, setProcesando] = useState(false);

  async function solicitar(libro: Libro) {
    if (!perfil) return;
    setSolicitando(libro.id_libro);
    setAviso(null);
    try {
      const p = await prestamosApi.solicitar(libro.id_libro);
      setAviso({
        tipo: "exito",
        texto: `Solicitud enviada: "${libro.titulo}" (ejemplar ${p.ejemplar_codigo}). La biblioteca la revisará y la verás en Mis préstamos.`,
      });
      libros.recargar();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
    } finally {
      setSolicitando(null);
    }
  }

  async function confirmarRetiro() {
    if (!retirando) return;
    setProcesando(true);
    try {
      await catalogoApi.retirarLibro(retirando.id_libro);
      setAviso({ tipo: "exito", texto: `"${retirando.titulo}" se retiró del catálogo.` });
      setRetirando(null);
      libros.recargar();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
      setRetirando(null);
    } finally {
      setProcesando(false);
    }
  }

  const hayFiltros = Boolean(busqueda || categoria || soloDisponibles);

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Catálogo</h1>
          <p>
            {libros.datos
              ? `${plural(libros.datos.length, "libro")}${hayFiltros ? " con estos filtros" : " en la biblioteca"}.`
              : "Busca por título, autor, ISBN o categoría."}
          </p>
        </div>
        {esEmpleado && (
          <button type="button" className="btn" onClick={() => setEditando("nuevo")}>
            Agregar libro
          </button>
        )}
      </header>

      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <div className="campo campo--corto">
          <label htmlFor="buscar-por">Buscar por</label>
          <select id="buscar-por" value={buscarPor} onChange={(e) => setBuscarPor(e.target.value as BuscarPor)}>
            {Object.entries(BUSQUEDAS).map(([valor, b]) => (
              <option key={valor} value={valor}>{b.etiqueta}</option>
            ))}
          </select>
        </div>
        <div className="campo campo--ancho">
          <label htmlFor="buscar">{BUSQUEDAS[buscarPor].etiqueta}</label>
          <input
            id="buscar"
            type="search"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder={BUSQUEDAS[buscarPor].ejemplo}
          />
        </div>
        <div className="campo">
          <label htmlFor="categoria">Categoría</label>
          <select id="categoria" value={categoria} onChange={(e) => setCategoria(e.target.value)}>
            <option value="">Todas</option>
            {categorias.datos?.map((c) => (
              <option key={c.id_categoria} value={c.id_categoria}>{c.nombre}</option>
            ))}
          </select>
        </div>
        <label className="casilla">
          <input type="checkbox" checked={soloDisponibles} onChange={(e) => setSoloDisponibles(e.target.checked)} />
          Solo con copias disponibles
        </label>
      </form>

      <Aviso aviso={aviso} onCerrar={() => setAviso(null)} />

      {libros.error && <ErrorCarga mensaje={libros.error} onReintentar={libros.recargar} />}
      {!libros.datos && libros.cargando && <Cargando texto="Cargando el catálogo…" />}

      {libros.datos && libros.datos.length === 0 && (
        <Vacio titulo={hayFiltros ? "Ningún libro coincide" : "El catálogo está vacío"}>
          <p>{hayFiltros ? "Prueba con otra palabra o quita algún filtro." : "Agrega el primer libro para empezar."}</p>
        </Vacio>
      )}

      {libros.datos && libros.datos.length > 0 && (
        <ul className="libros" aria-busy={libros.cargando}>
          {libros.datos.map((libro) => {
            const disponibles = libro.ejemplares_disponibles ?? 0;
            const total = libro.ejemplares_total ?? 0;
            return (
              <li key={libro.id_libro} className="libro">
                <div>
                  <h2 className="libro-titulo">{libro.titulo}</h2>
                  <p className="libro-autores">{libro.autores_detalle.map((a) => a.nombre).join(", ")}</p>
                  <p className="libro-meta">
                    {libro.editorial_nombre}, {libro.anio}. {libro.categoria_nombre}. ISBN {libro.isbn}
                  </p>
                  {libro.descripcion && <p className="libro-descripcion">{libro.descripcion}</p>}
                </div>

                <div className="libro-lado">
                  <p className={disponibles > 0 ? "disponibilidad" : "disponibilidad disponibilidad--agotado"}>
                    {total === 0
                      ? "Sin ejemplares registrados"
                      : disponibles > 0
                        ? `${disponibles} de ${total} ${disponibles === 1 ? "disponible" : "disponibles"}`
                        : "Todas las copias prestadas"}
                  </p>

                  {esEmpleado ? (
                    <div className="acciones">
                      <Link className="btn btn--secundario btn--pequeno" to={`/ejemplares?libro=${libro.id_libro}`}>
                        Ver ejemplares
                      </Link>
                      <button type="button" className="btn btn--secundario btn--pequeno" onClick={() => setEditando(libro)}>
                        Editar
                      </button>
                      <button type="button" className="btn btn--texto-peligro btn--pequeno" onClick={() => setRetirando(libro)}>
                        Retirar
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      className="btn"
                      disabled={disponibles === 0 || solicitando !== null}
                      onClick={() => solicitar(libro)}
                    >
                      {solicitando === libro.id_libro ? "Enviando…" : "Solicitar préstamo"}
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <Dialogo
        abierto={editando !== null}
        titulo={editando === "nuevo" ? "Agregar libro" : "Editar libro"}
        onCerrar={() => setEditando(null)}
      >
        <FormLibro
          libro={editando === "nuevo" ? null : editando}
          onCancelar={() => setEditando(null)}
          onGuardado={(l) => {
            setAviso({ tipo: "exito", texto: editando === "nuevo" ? `"${l.titulo}" se agregó al catálogo.` : `Se guardaron los cambios de "${l.titulo}".` });
            setEditando(null);
            libros.recargar();
          }}
        />
      </Dialogo>

      <Dialogo abierto={retirando !== null} titulo="Retirar del catálogo" onCerrar={() => setRetirando(null)}>
        <div className="dialogo-cuerpo">
          <p>
            <strong>{retirando?.titulo}</strong> dejará de aparecer en el catálogo. Su historial de préstamos se conserva.
          </p>
        </div>
        <div className="dialogo-pie">
          <button type="button" className="btn btn--secundario" onClick={() => setRetirando(null)}>Cancelar</button>
          <button type="button" className="btn btn--peligro" disabled={procesando} onClick={confirmarRetiro}>
            {procesando ? "Retirando…" : "Retirar libro"}
          </button>
        </div>
      </Dialogo>
    </>
  );
}
