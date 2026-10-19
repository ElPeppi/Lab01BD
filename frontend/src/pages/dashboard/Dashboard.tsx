import { Link } from "react-router-dom";
import { multasApi } from "../../api/devoluciones";
import { ejemplaresApi } from "../../api/ejemplares";
import { prestamosApi } from "../../api/prestamos";
import { useAuth } from "../../auth/AuthContext";
import { ErrorCarga } from "../../components/Estados";
import { EstadoPrestamo } from "../../components/EtiquetaEstado";
import { useConsulta } from "../../hooks/useConsulta";
import { formatearFecha, formatearPesos } from "../../utils/formato";

const solicitudes = () => prestamosApi.listar({ estado: "solicitado" });
const activos = () => prestamosApi.listar({ activos: true });
const multasPendientes = () => multasApi.listar({ pagada: false });

/** Inicio del personal: lo que requiere atención hoy. */
export default function Dashboard() {
  const { perfil } = useAuth();
  // Las cuatro consultas salen en paralelo
  const pendientes = useConsulta(solicitudes);
  const prestados = useConsulta(activos);
  const inventario = useConsulta(ejemplaresApi.resumenInventario);
  const multas = useConsulta(multasPendientes);
  const porCobrar = multas.datos?.reduce((t, m) => t + Number(m.monto), 0);

  const vencidos = (prestados.datos ?? [])
    .filter((p) => p.vencido)
    .sort((a, b) => b.dias_retraso - a.dias_retraso);
  const nombre = perfil?.nombre.replace(/\s*\(.*\)\s*$/, "").split(" ")[0];
  const cifra = (n: number | undefined) => (n === undefined ? "…" : n);

  return (
    <>
      <header className="encabezado">
        <div>
          <h1>Hola, {nombre}</h1>
          <p>Esto es lo que requiere atención en la biblioteca.</p>
        </div>
      </header>

      {[pendientes.error, prestados.error, inventario.error, multas.error].filter(Boolean).slice(0, 1).map((e) => (
        <ErrorCarga
          key="err"
          mensaje={e as string}
          onReintentar={() => {
            pendientes.recargar();
            prestados.recargar();
            inventario.recargar();
            multas.recargar();
          }}
        />
      ))}

      <dl className="cifras">
        <div className="cifra"><dt>Solicitudes por revisar</dt><dd>{cifra(pendientes.datos?.length)}</dd></div>
        <div className="cifra"><dt>Libros prestados</dt><dd>{cifra(prestados.datos?.length)}</dd></div>
        <div className={vencidos.length ? "cifra cifra--aviso" : "cifra"}><dt>Préstamos vencidos</dt><dd>{prestados.datos ? vencidos.length : "…"}</dd></div>
        <div className="cifra">
          <dt>Ejemplares disponibles</dt>
          <dd>
            {cifra(inventario.datos?.disponibles)}
            {inventario.datos && <span className="cifra-total"> de {inventario.datos.total}</span>}
          </dd>
        </div>
        <div className="cifra">
          <dt>Multas por cobrar</dt>
          <dd>
            {porCobrar === undefined ? "…" : formatearPesos(porCobrar)}
            {multas.datos && multas.datos.length > 0 && <span className="cifra-total"> en {multas.datos.length}</span>}
          </dd>
        </div>
      </dl>

      <div className="rejilla-2">
        <section className="panel" aria-labelledby="t-solicitudes">
          <div className="panel-cabecera">
            <h2 id="t-solicitudes">Solicitudes por revisar</h2>
            <Link to="/prestamos">Revisar</Link>
          </div>
          {pendientes.datos?.length === 0 && <p className="texto-suave">No hay solicitudes pendientes.</p>}
          <ul className="lista-simple">
            {pendientes.datos?.slice(0, 5).map((p) => (
              <li key={p.id_prestamo}>
                <span>
                  <strong>{p.libro_titulo}</strong>
                  <span className="celda-secundaria">{p.usuario_nombres}, {formatearFecha(p.fecha_solicitud)}</span>
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section className="panel" aria-labelledby="t-vencidos">
          <div className="panel-cabecera">
            <h2 id="t-vencidos">Préstamos vencidos</h2>
            <Link to="/devoluciones">Ver devoluciones</Link>
          </div>
          {prestados.datos && vencidos.length === 0 && <p className="texto-suave">Ningún préstamo está vencido.</p>}
          <ul className="lista-simple">
            {vencidos.slice(0, 5).map((p) => (
              <li key={p.id_prestamo}>
                <span>
                  <strong>{p.libro_titulo}</strong>
                  <span className="celda-secundaria">{p.usuario_nombres}, venció el {formatearFecha(p.fecha_vencimiento)}</span>
                </span>
                <EstadoPrestamo prestamo={p} />
              </li>
            ))}
          </ul>
        </section>
      </div>
    </>
  );
}
