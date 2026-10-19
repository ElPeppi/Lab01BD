export type AvisoDatos = { tipo: "exito" | "error"; texto: string };

/** Mensaje tras una acción (aprobar, guardar, etc.). Los lectores de pantalla lo anuncian. */
export default function Aviso({ aviso, onCerrar }: { aviso: AvisoDatos | null; onCerrar: () => void }) {
  if (!aviso) return null;
  return (
    <div
      className={`alerta alerta--${aviso.tipo} alerta--accion`}
      role={aviso.tipo === "error" ? "alert" : "status"}
    >
      <span>{aviso.texto}</span>
      <button type="button" className="btn-icono btn-icono--suave" aria-label="Cerrar aviso" onClick={onCerrar}>
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  );
}
