import { useCallback, useEffect, useState } from "react";
import { mensajeError } from "../api/errores";

type Estado<T> = { datos: T | undefined; error: string | null; cargando: boolean };

/**
 * Ejecuta una consulta GET y expone { datos, error, cargando, recargar }.
 * La `consulta` debe ser estable (useCallback o función de módulo): cuando cambia
 * (p. ej. cambian los filtros) se vuelve a pedir, sin borrar los datos anteriores
 * mientras llega la respuesta nueva. Si llega una respuesta vieja tarde, se descarta.
 */
export function useConsulta<T>(consulta: () => Promise<T>) {
  const [estado, setEstado] = useState<Estado<T>>({ datos: undefined, error: null, cargando: true });
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let vigente = true;
    consulta()
      .then((datos) => vigente && setEstado({ datos, error: null, cargando: false }))
      .catch((err) => vigente && setEstado((s) => ({ ...s, error: mensajeError(err), cargando: false })));
    return () => {
      vigente = false;
    };
  }, [consulta, version]);

  const recargar = useCallback(() => {
    setEstado((s) => ({ ...s, cargando: true }));
    setVersion((v) => v + 1);
  }, []);

  return { ...estado, recargar };
}
