import { useEffect, useState } from "react";

/** Devuelve `valor` solo cuando deja de cambiar durante `ms` (evita una petición por tecla). */
export function useDebounce<T>(valor: T, ms = 300) {
  const [estable, setEstable] = useState(valor);
  useEffect(() => {
    const t = setTimeout(() => setEstable(valor), ms);
    return () => clearTimeout(t);
  }, [valor, ms]);
  return estable;
}
