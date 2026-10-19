import { useCallback, useState } from "react";
import { reportesApi } from "../../api/reportes";
import { Cargando, ErrorCarga, Vacio } from "../../components/Estados";
import { useConsulta } from "../../hooks/useConsulta";
import { formatearFecha, formatearPesos, plural } from "../../utils/formato";
import "./Reportes.css";

type TabReporte = "resumen" | "populares" | "morosos" | "multas" | "usuarios";

export default function Reportes() {
  const [tab, setTab] = useState<TabReporte>("resumen");
  const [exportando, setExportando] = useState(false);

  // Estados de filtros
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [limite, setLimite] = useState(10);
  const [diasMinimos, setDiasMinimos] = useState(0);
  const [filtroPagada, setFiltroPagada] = useState<string>("todas");
  const [rolUsuario, setRolUsuario] = useState<string>("");

  // Consultas según pestaña
  const consultaResumen = useConsulta(reportesApi.resumen);

  const consultarPopulares = useCallback(
    () => reportesApi.librosPopulares({ desde: desde || undefined, hasta: hasta || undefined, limit: limite }),
    [desde, hasta, limite]
  );
  const consultaPopulares = useConsulta(consultarPopulares);

  const consultarMorosos = useCallback(
    () => reportesApi.morosos({ dias_minimos: diasMinimos || undefined }),
    [diasMinimos]
  );
  const consultaMorosos = useConsulta(consultarMorosos);

  const consultarMultas = useCallback(
    () =>
      reportesApi.multasRecaudo({
        desde: desde || undefined,
        hasta: hasta || undefined,
        pagada: filtroPagada === "todas" ? undefined : filtroPagada === "true",
      }),
    [desde, hasta, filtroPagada]
  );
  const consultaMultas = useConsulta(consultarMultas);

  const consultarUsuarios = useCallback(
    () => reportesApi.usuariosActividad({ rol: rolUsuario || undefined, limit: limite }),
    [rolUsuario, limite]
  );
  const consultaUsuarios = useConsulta(consultarUsuarios);

  const handleDescargar = async (tipo: "libros-populares" | "morosos" | "multas") => {
    try {
      setExportando(true);
      await reportesApi.descargarCSV(tipo);
    } catch {
      alert("Error al descargar el archivo CSV");
    } finally {
      setExportando(false);
    }
  };

  return (
    <div>
      <header className="encabezado">
        <div>
          <h1>Módulo de Reportes</h1>
          <p>Métricas consolidadas, análisis de préstamos, morosidad y finanzas de la biblioteca.</p>
        </div>
      </header>

      {/* Navegación por pestañas */}
      <div className="segmentos" role="tablist" aria-label="Secciones de reportes">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "resumen"}
          aria-pressed={tab === "resumen"}
          onClick={() => setTab("resumen")}
        >
          Indicadores Generales
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "populares"}
          aria-pressed={tab === "populares"}
          onClick={() => setTab("populares")}
        >
          Libros Populares
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "morosos"}
          aria-pressed={tab === "morosos"}
          onClick={() => setTab("morosos")}
        >
          Préstamos Vencidos (Mora)
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "multas"}
          aria-pressed={tab === "multas"}
          onClick={() => setTab("multas")}
        >
          Recaudo y Multas
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "usuarios"}
          aria-pressed={tab === "usuarios"}
          onClick={() => setTab("usuarios")}
        >
          Actividad de Usuarios
        </button>
      </div>

      {/* PESTAÑA: RESUMEN / KPIS */}
      {tab === "resumen" && (
        <section>
          {consultaResumen.cargando && <Cargando />}
          {consultaResumen.error && (
            <ErrorCarga mensaje={consultaResumen.error} onReintentar={consultaResumen.recargar} />
          )}
          {consultaResumen.datos && (
            <div className="reportes-tarjetas">
              <div className="reportes-tarjeta">
                <h3>Libros e Inventario</h3>
                <div className="valor">{consultaResumen.datos.libros.total}</div>
                <div className="subvalores">
                  <span><strong>{consultaResumen.datos.ejemplares.total}</strong> ejemplares totales</span>
                  <span><strong>{consultaResumen.datos.ejemplares.disponibles}</strong> disponibles</span>
                  <span><strong>{consultaResumen.datos.ejemplares.prestados}</strong> prestados</span>
                  <span><strong>{consultaResumen.datos.ejemplares.perdidos}</strong> perdidos</span>
                </div>
              </div>

              <div className="reportes-tarjeta">
                <h3>Préstamos Activos</h3>
                <div className="valor">{consultaResumen.datos.prestamos.aprobados}</div>
                <div className="subvalores">
                  <span><strong>{consultaResumen.datos.prestamos.solicitados}</strong> solicitudes pendientes</span>
                  <span><strong>{consultaResumen.datos.prestamos.vencidos}</strong> con fecha vencida</span>
                  <span><strong>{consultaResumen.datos.prestamos.devueltos}</strong> devueltos históricamente</span>
                  <span><strong>{consultaResumen.datos.prestamos.total}</strong> solicitudes en total</span>
                </div>
              </div>

              <div className="reportes-tarjeta">
                <h3>Control de Multas</h3>
                <div className="valor">
                  {formatearPesos(consultaResumen.datos.multas.monto_total)}
                </div>
                <div className="subvalores">
                  <span>Recaudado: <strong>{formatearPesos(consultaResumen.datos.multas.monto_pagado)}</strong> ({consultaResumen.datos.multas.pagadas} pagadas)</span>
                  <span>Pendiente: <strong>{formatearPesos(consultaResumen.datos.multas.monto_pendiente)}</strong> ({consultaResumen.datos.multas.pendientes} pendientes)</span>
                </div>
              </div>

              <div className="reportes-tarjeta">
                <h3>Usuarios Registrados</h3>
                <div className="valor">{consultaResumen.datos.usuarios.total}</div>
                <div className="subvalores">
                  <span><strong>{consultaResumen.datos.usuarios.activos}</strong> usuarios activos</span>
                  <span><strong>{consultaResumen.datos.usuarios.bloqueados}</strong> usuarios bloqueados</span>
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* PESTAÑA: LIBROS POPULARES */}
      {tab === "populares" && (
        <section>
          <div className="filtros">
            <div className="campo campo--corto">
              <label htmlFor="pop-desde">Desde</label>
              <input
                id="pop-desde"
                type="date"
                value={desde}
                onChange={(e) => setDesde(e.target.value)}
              />
            </div>
            <div className="campo campo--corto">
              <label htmlFor="pop-hasta">Hasta</label>
              <input
                id="pop-hasta"
                type="date"
                value={hasta}
                onChange={(e) => setHasta(e.target.value)}
              />
            </div>
            <div className="campo campo--corto">
              <label htmlFor="pop-limite">Límite</label>
              <select
                id="pop-limite"
                value={limite}
                onChange={(e) => setLimite(Number(e.target.value))}
              >
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={20}>Top 20</option>
                <option value={50}>Top 50</option>
              </select>
            </div>
            <button
              type="button"
              className="btn btn--secundario"
              disabled={exportando}
              onClick={() => handleDescargar("libros-populares")}
            >
              Exportar CSV
            </button>
          </div>

          {consultaPopulares.cargando && <Cargando />}
          {consultaPopulares.error && (
            <ErrorCarga mensaje={consultaPopulares.error} onReintentar={consultaPopulares.recargar} />
          )}
          {consultaPopulares.datos && consultaPopulares.datos.length === 0 && (
            <Vacio titulo="Sin datos">
              <p>No se encontraron registros de préstamos para el periodo seleccionado.</p>
            </Vacio>
          )}
          {consultaPopulares.datos && consultaPopulares.datos.length > 0 && (
            <div className="tabla-contenedor">
              <table className="tabla">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Título</th>
                    <th>ISBN</th>
                    <th>Categoría</th>
                    <th>Editorial</th>
                    <th className="num">Préstamos</th>
                    <th className="num">Activos</th>
                    <th className="num">Disponibles / Total</th>
                  </tr>
                </thead>
                <tbody>
                  {consultaPopulares.datos.map((item, idx) => (
                    <tr key={item.id_libro}>
                      <td>
                        <span
                          className={`reportes-ranking ${
                            idx === 0
                              ? "reportes-ranking--oro"
                              : idx === 1
                              ? "reportes-ranking--plata"
                              : idx === 2
                              ? "reportes-ranking--bronce"
                              : ""
                          }`}
                        >
                          {idx + 1}
                        </span>
                      </td>
                      <td><strong>{item.titulo}</strong></td>
                      <td>{item.isbn}</td>
                      <td>{item.categoria ?? "—"}</td>
                      <td>{item.editorial ?? "—"}</td>
                      <td className="num"><strong>{item.total_prestamos}</strong></td>
                      <td className="num">{item.prestamos_activos}</td>
                      <td className="num">{item.ejemplares_disponibles} / {item.ejemplares_totales}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {/* PESTAÑA: MOROSOS */}
      {tab === "morosos" && (
        <section>
          <div className="filtros">
            <div className="campo campo--corto">
              <label htmlFor="mor-dias">Días mínimos de mora</label>
              <input
                id="mor-dias"
                type="number"
                min="0"
                value={diasMinimos}
                onChange={(e) => setDiasMinimos(Math.max(0, Number(e.target.value)))}
              />
            </div>
            <button
              type="button"
              className="btn btn--secundario"
              disabled={exportando}
              onClick={() => handleDescargar("morosos")}
            >
              Exportar CSV
            </button>
          </div>

          {consultaMorosos.cargando && <Cargando />}
          {consultaMorosos.error && (
            <ErrorCarga mensaje={consultaMorosos.error} onReintentar={consultaMorosos.recargar} />
          )}
          {consultaMorosos.datos && consultaMorosos.datos.morosos.length === 0 && (
            <Vacio titulo="Excelente">
              <p>No hay usuarios con préstamos vencidos en este momento.</p>
            </Vacio>
          )}
          {consultaMorosos.datos && consultaMorosos.datos.morosos.length > 0 && (
            <>
              <div className="alerta alerta--aviso">
                Hay <strong>{consultaMorosos.datos.total_morosos}</strong> préstamos vencidos.
                Multa total proyectada: <strong>{formatearPesos(consultaMorosos.datos.total_multa_estimada)}</strong> (Tarifa: {formatearPesos(consultaMorosos.datos.tarifa_dia)}/día).
              </div>
              <div className="tabla-contenedor">
                <table className="tabla">
                  <thead>
                    <tr>
                      <th>Usuario</th>
                      <th>Código</th>
                      <th>Libro / Ejemplar</th>
                      <th>Fecha Préstamo</th>
                      <th>Fecha Vencimiento</th>
                      <th className="num">Días Retraso</th>
                      <th className="num">Multa Estimada</th>
                    </tr>
                  </thead>
                  <tbody>
                    {consultaMorosos.datos.morosos.map((m) => (
                      <tr key={m.id_prestamo}>
                        <td>
                          <strong>{m.usuario.nombres}</strong>
                          <div className="texto-suave" style={{ fontSize: "0.8125rem" }}>
                            {m.usuario.correo} {m.usuario.carrera ? `• ${m.usuario.carrera}` : ""}
                          </div>
                        </td>
                        <td>{m.usuario.codigo}</td>
                        <td>
                          <div><strong>{m.ejemplar.libro_titulo}</strong></div>
                          <div className="texto-suave" style={{ fontSize: "0.8125rem" }}>
                            Ejemplar: {m.ejemplar.codigo_barras} ({m.ejemplar.ubicacion})
                          </div>
                        </td>
                        <td>{formatearFecha(m.fecha_prestamo)}</td>
                        <td>
                          <span className="estado estado--vencido">
                            {formatearFecha(m.fecha_vencimiento)}
                          </span>
                        </td>
                        <td className="num">
                          <strong style={{ color: "var(--error)" }}>
                            {plural(m.dias_retraso, "día")}
                          </strong>
                        </td>
                        <td className="num">
                          <strong>{formatearPesos(m.multa_estimada)}</strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      )}

      {/* PESTAÑA: MULTAS Y RECAUDO */}
      {tab === "multas" && (
        <section>
          <div className="filtros">
            <div className="campo campo--corto">
              <label htmlFor="mul-desde">Desde</label>
              <input
                id="mul-desde"
                type="date"
                value={desde}
                onChange={(e) => setDesde(e.target.value)}
              />
            </div>
            <div className="campo campo--corto">
              <label htmlFor="mul-hasta">Hasta</label>
              <input
                id="mul-hasta"
                type="date"
                value={hasta}
                onChange={(e) => setHasta(e.target.value)}
              />
            </div>
            <div className="campo campo--corto">
              <label htmlFor="mul-estado">Estado de Pago</label>
              <select
                id="mul-estado"
                value={filtroPagada}
                onChange={(e) => setFiltroPagada(e.target.value)}
              >
                <option value="todas">Todas</option>
                <option value="true">Solo Pagadas</option>
                <option value="false">Solo Pendientes</option>
              </select>
            </div>
            <button
              type="button"
              className="btn btn--secundario"
              disabled={exportando}
              onClick={() => handleDescargar("multas")}
            >
              Exportar CSV
            </button>
          </div>

          {consultaMultas.cargando && <Cargando />}
          {consultaMultas.error && (
            <ErrorCarga mensaje={consultaMultas.error} onReintentar={consultaMultas.recargar} />
          )}
          {consultaMultas.datos && (
            <>
              <div className="reportes-tarjetas">
                <div className="reportes-tarjeta">
                  <h3>Total Facturado</h3>
                  <div className="valor">{formatearPesos(consultaMultas.datos.resumen.monto_total)}</div>
                  <div className="subvalores">
                    <span>{consultaMultas.datos.resumen.total_multas} multas emitidas</span>
                  </div>
                </div>
                <div className="reportes-tarjeta">
                  <h3>Total Recaudado</h3>
                  <div className="valor" style={{ color: "var(--primario)" }}>
                    {formatearPesos(consultaMultas.datos.resumen.monto_pagado)}
                  </div>
                  <div className="subvalores">
                    <span>{consultaMultas.datos.resumen.pagadas_count} multas pagadas</span>
                  </div>
                </div>
                <div className="reportes-tarjeta">
                  <h3>Saldo Pendiente</h3>
                  <div className="valor" style={{ color: "var(--error)" }}>
                    {formatearPesos(consultaMultas.datos.resumen.monto_pendiente)}
                  </div>
                  <div className="subvalores">
                    <span>{consultaMultas.datos.resumen.pendientes_count} multas pendientes</span>
                  </div>
                </div>
              </div>

              {consultaMultas.datos.multas.length === 0 ? (
                <Vacio titulo="Sin multas">
                  <p>No se encontraron multas en el periodo seleccionado.</p>
                </Vacio>
              ) : (
                <div className="tabla-contenedor">
                  <table className="tabla">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Libro</th>
                        <th>Fecha Devolución</th>
                        <th>Estado</th>
                        <th>Fecha Pago</th>
                        <th className="num">Monto</th>
                      </tr>
                    </thead>
                    <tbody>
                      {consultaMultas.datos.multas.map((m) => (
                        <tr key={m.id_multa}>
                          <td>#{m.id_multa}</td>
                          <td>
                            <strong>{m.usuario_nombres}</strong> ({m.usuario_codigo})
                          </td>
                          <td>{m.libro_titulo}</td>
                          <td>{m.fecha_devolucion ? formatearFecha(m.fecha_devolucion) : "—"}</td>
                          <td>
                            <span className={m.pagada ? "estado estado--pagada" : "estado estado--pendiente"}>
                              {m.pagada ? "Pagada" : "Pendiente"}
                            </span>
                          </td>
                          <td>{m.fecha_pago ? formatearFecha(m.fecha_pago) : "—"}</td>
                          <td className="num"><strong>{formatearPesos(m.monto)}</strong></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </section>
      )}

      {/* PESTAÑA: ACTIVIDAD DE USUARIOS */}
      {tab === "usuarios" && (
        <section>
          <div className="filtros">
            <div className="campo campo--corto">
              <label htmlFor="usr-rol">Tipo de usuario</label>
              <select
                id="usr-rol"
                value={rolUsuario}
                onChange={(e) => setRolUsuario(e.target.value)}
              >
                <option value="">Todos</option>
                <option value="estudiante">Estudiantes</option>
                <option value="docente">Docentes</option>
              </select>
            </div>
            <div className="campo campo--corto">
              <label htmlFor="usr-limite">Límite</label>
              <select
                id="usr-limite"
                value={limite}
                onChange={(e) => setLimite(Number(e.target.value))}
              >
                <option value={10}>Top 10</option>
                <option value={20}>Top 20</option>
                <option value={50}>Top 50</option>
              </select>
            </div>
          </div>

          {consultaUsuarios.cargando && <Cargando />}
          {consultaUsuarios.error && (
            <ErrorCarga mensaje={consultaUsuarios.error} onReintentar={consultaUsuarios.recargar} />
          )}
          {consultaUsuarios.datos && consultaUsuarios.datos.length === 0 && (
            <Vacio titulo="Sin usuarios">
              <p>No se encontraron usuarios con actividad registrada.</p>
            </Vacio>
          )}
          {consultaUsuarios.datos && consultaUsuarios.datos.length > 0 && (
            <div className="tabla-contenedor">
              <table className="tabla">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Código</th>
                    <th>Rol / Carrera</th>
                    <th>Estado</th>
                    <th className="num">Préstamos Totales</th>
                    <th className="num">Préstamos Activos</th>
                    <th className="num">Multas</th>
                    <th className="num">Monto Multas</th>
                  </tr>
                </thead>
                <tbody>
                  {consultaUsuarios.datos.map((u) => (
                    <tr key={u.id_usuario}>
                      <td>
                        <strong>{u.nombres}</strong>
                        <div className="texto-suave" style={{ fontSize: "0.8125rem" }}>{u.correo}</div>
                      </td>
                      <td>{u.codigo}</td>
                      <td>
                        <div style={{ textTransform: "capitalize" }}>{u.rol}</div>
                        <div className="texto-suave" style={{ fontSize: "0.8125rem" }}>{u.carrera ?? "—"}</div>
                      </td>
                      <td>
                        <span className={`estado estado--${u.estado}`}>
                          {u.estado}
                        </span>
                      </td>
                      <td className="num"><strong>{u.total_prestamos}</strong></td>
                      <td className="num">{u.prestamos_activos}</td>
                      <td className="num">{u.multas_count}</td>
                      <td className="num">
                        {Number(u.total_monto_multas) > 0 ? (
                          <span style={{ color: "var(--error)", fontWeight: 600 }}>
                            {formatearPesos(u.total_monto_multas)}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
