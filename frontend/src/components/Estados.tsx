import type { ReactNode } from "react";

export function Cargando({ texto = "Cargando…" }: { texto?: string }) {
  return (
    <p className="cargando" role="status">
      {texto}
    </p>
  );
}

export function ErrorCarga({ mensaje, onReintentar }: { mensaje: string; onReintentar?: () => void }) {
  return (
    <div className="alerta alerta--error alerta--accion" role="alert">
      <span>{mensaje}</span>
      {onReintentar && (
        <button type="button" className="btn btn--secundario btn--pequeno" onClick={onReintentar}>
          Reintentar
        </button>
      )}
    </div>
  );
}

export function Vacio({ titulo, children }: { titulo: string; children?: ReactNode }) {
  return (
    <div className="vacio">
      <h2>{titulo}</h2>
      {children}
    </div>
  );
}
