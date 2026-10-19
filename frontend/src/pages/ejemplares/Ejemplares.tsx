import { useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { catalogoApi } from "../../api/catalogo";
import { ejemplaresApi } from "../../api/ejemplares";
import { mensajeError } from "../../api/errores";
import type { Ejemplar, EstadoEjemplar } from "../../api/tipos";
import Aviso, { type AvisoDatos } from "../../components/Aviso";
import Dialogo from "../../components/Dialogo";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { EtiquetaEstado } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { useDebounce } from "../../hooks/useDebounce";
import { plural } from "../../utils/formato";
import FormEjemplar from "./FormEjemplar";

const todosLosLibros = () => catalogoApi.libros();

export default function Ejemplares() {
  // ?libro=ID permite llegar filtrado desde el Catálogo ("Ver ejemplares")
  const [params, setParams] = useSearchParams();
  const libro = params.get("libro") ?? "";
  const [texto, setTexto] = useState("");
  const [estado, setEstado] = useState<EstadoEjemplar | "">("");
  const q = useDebounce(texto.trim(), 300);

  const consulta = useCallback(
    () => ejemplaresApi.listar({ q, estado: estado || undefined, libro: libro ? Number(libro) : undefined }),
    [q, estado, libro],
  );
  const ejemplares = useConsulta(consulta);
  const resumen = useConsulta(ejemplaresApi.resumenInventario);
  const libros = useConsulta(todosLosLibros);

  const [aviso, setAviso] = useState<AvisoDatos | null>(null);
  const [editando, setEditando] = useState<Ejemplar | "nuevo" | null>(null);
  const [bajando, setBajando] = useState<Ejemplar | null>(null);
  const [procesando, setProcesando] = useState(false);

  function cambiarLibro(valor: string) {
    const siguiente = new URLSearchParams(params);
    if (valor) siguiente.set("libro", valor);
    else siguiente.delete("libro");
    setParams(siguiente, { replace: true });
  }

  function recargarTodo() {
    ejemplares.recargar();
    resumen.recargar();
  }

  async function confirmarBaja() {
    if (!bajando) return;
    setProcesando(true);
    try {
      await ejemplaresApi.darDeBaja(bajando.id_ejemplar);
      setAviso({ tipo: "exito", texto: `El ejemplar ${bajando.codigo_barras} se dio de baja.` });
      recargarTodo();
    } catch (err) {
      setAviso({ tipo: "error", texto: mensajeError(err) });
    } finally {
      setBajando(null);
      setProcesando(false);
    }
  }

  const r = resumen.datos;

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Ejemplares</h1>
          <p>Las copias físicas de cada libro: dónde están y en qué estado.</p>
        </div>
        <button type="button" className="btn" onClick={() => setEditando("nuevo")} disabled={!libros.datos}>
          Registrar ejemplar
        </button>
      </header>

      {r && (
        <dl className="cifras cifras--compactas" aria-label="Inventario">
          <div className="cifra"><dt>En inventario</dt><dd>{r.total}</dd></div>
          <div className="cifra"><dt>Disponibles</dt><dd>{r.disponibles}</dd></div>
          <div className="cifra"><dt>Prestados</dt><dd>{r.prestados}</dd></div>
          <div className="cifra"><dt>Perdidos</dt><dd>{r.perdidos}</dd></div>
          <div className="cifra"><dt>Dañados</dt><dd>{r.danados}</dd></div>
        </dl>
      )}

      <form className="filtros" role="search" onSubmit={(e) => e.preventDefault()}>
        <div className="campo campo--ancho">
          <label htmlFor="ej-buscar">Buscar</label>
          <input id="ej-buscar" type="search" value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Código, título o ubicación" />
        </div>
        <div className="campo">
          <label htmlFor="ej-filtro-libro">Libro</label>
          <select id="ej-filtro-libro" value={libro} onChange={(e) => cambiarLibro(e.target.value)}>
            <option value="">Todos</option>
            {libros.datos?.map((l) => (
              <option key={l.id_libro} value={l.id_libro}>{l.titulo}</option>
            ))}
          </select>
        </div>
        <div className="campo campo--corto">
          <label htmlFor="ej-filtro-estado">Estado</label>
          <select id="ej-filtro-estado" value={estado} onChange={(e) => setEstado(e.target.value as EstadoEjemplar | "")}>
            <option value="">Todos</option>
            <option value="disponible">Disponible</option>
            <option value="prestado">Prestado</option>
            <option value="perdido">Perdido</option>
          </select>
        </div>
      </form>

      <Aviso aviso={aviso} onCerrar={() => setAviso(null)} />
      {ejemplares.error && <ErrorCarga mensaje={ejemplares.error} onReintentar={ejemplares.recargar} />}
      {!ejemplares.datos && ejemplares.cargando && <Cargando texto="Cargando ejemplares…" />}

      {ejemplares.datos && ejemplares.datos.length === 0 && (
        <Vacio titulo="No hay ejemplares con estos filtros">
          <p>Cambia la búsqueda o registra un ejemplar nuevo.</p>
        </Vacio>
      )}

      {ejemplares.datos && ejemplares.datos.length > 0 && (
        <>
          <p className="texto-suave conteo">{plural(ejemplares.datos.length, "ejemplar", "ejemplares")}</p>
          <div className="tabla-contenedor" aria-busy={ejemplares.cargando}>
            <table className="tabla">
              <thead>
                <tr>
                  <th scope="col">Código</th>
                  <th scope="col">Libro</th>
                  <th scope="col">Ubicación</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Condición</th>
                  <th scope="col"><span className="sr-only">Acciones</span></th>
                </tr>
              </thead>
              <tbody>
                {ejemplares.datos.map((ej) => (
                  <tr key={ej.id_ejemplar}>
                    <td className="tabular">{ej.codigo_barras}</td>
                    <td>{ej.libro_titulo}</td>
                    <td>{ej.ubicacion}</td>
                    <td><EtiquetaEstado estado={ej.estado} /></td>
                    <td>{ej.condicion === "danado" ? <EtiquetaEstado estado="danado" /> : "Bueno"}</td>
                    <td>
                      <div className="acciones acciones--fin">
                        <button type="button" className="btn btn--texto btn--pequeno" onClick={() => setEditando(ej)}>
                          Editar
                        </button>
                        <button
                          type="button"
                          className="btn btn--texto-peligro btn--pequeno"
                          onClick={() => setBajando(ej)}
                          disabled={ej.estado === "prestado"}
                          title={ej.estado === "prestado" ? "No se puede dar de baja mientras está prestado" : undefined}
                        >
                          Dar de baja
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <Dialogo
        abierto={editando !== null}
        titulo={editando === "nuevo" ? "Registrar ejemplar" : `Editar ${editando?.codigo_barras ?? ""}`}
        onCerrar={() => setEditando(null)}
      >
        <FormEjemplar
          ejemplar={editando === "nuevo" ? null : editando}
          libros={libros.datos ?? []}
          libroInicial={libro ? Number(libro) : undefined}
          onCancelar={() => setEditando(null)}
          onGuardado={(ej) => {
            setAviso({ tipo: "exito", texto: editando === "nuevo" ? `Se registró el ejemplar ${ej.codigo_barras}.` : `Se guardaron los cambios de ${ej.codigo_barras}.` });
            setEditando(null);
            recargarTodo();
          }}
        />
      </Dialogo>

      <Dialogo abierto={bajando !== null} titulo="Dar de baja el ejemplar" onCerrar={() => setBajando(null)}>
        <div className="dialogo-cuerpo">
          <p>
            El ejemplar <strong>{bajando?.codigo_barras}</strong> de <em>{bajando?.libro_titulo}</em> dejará de contar en el inventario y no se podrá prestar.
          </p>
        </div>
        <div className="dialogo-pie">
          <button type="button" className="btn btn--secundario" onClick={() => setBajando(null)}>Cancelar</button>
          <button type="button" className="btn btn--peligro" disabled={procesando} onClick={confirmarBaja}>
            {procesando ? "Procesando…" : "Dar de baja"}
          </button>
        </div>
      </Dialogo>
    </>
  );
}

