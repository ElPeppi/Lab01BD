import { useEffect, useId, useRef, type ReactNode } from "react";

type Props = {
  abierto: boolean;
  titulo: string;
  onCerrar: () => void;
  children: ReactNode; // cuerpo + pie (usar .dialogo-cuerpo y .dialogo-pie)
};

/**
 * Ventana modal con el <dialog> nativo del navegador: atrapa el foco, cierra con
 * Escape y bloquea la página de atrás sin librerías. El contenido solo se monta
 * mientras está abierto, así cada vez que se abre el formulario empieza limpio.
 */
export default function Dialogo({ abierto, titulo, onCerrar, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const idTitulo = useId();

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (abierto && !d.open) d.showModal();
    if (!abierto && d.open) d.close();
  }, [abierto]);

  return (
    <dialog
      ref={ref}
      className="dialogo"
      aria-labelledby={idTitulo}
      onClose={onCerrar}
      onCancel={(e) => {
        e.preventDefault(); // Escape: dejamos que React decida cerrar
        onCerrar();
      }}
    >
      {abierto && (
        <>
          <div className="dialogo-cabecera">
            <h2 id={idTitulo}>{titulo}</h2>
            <button type="button" className="btn-icono" aria-label="Cerrar" onClick={onCerrar}>
              <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>
          </div>
          {children}
        </>
      )}
    </dialog>
  );
}
