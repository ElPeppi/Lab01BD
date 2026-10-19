import { useState, type FormEvent } from "react";
import { erroresDeCampo, mensajeError } from "../../api/errores";
import { usuariosApi, type RolUsuario, type Usuario } from "../../api/usuarios";

type Props = {
  onGuardado: (u: Usuario) => void;
  onCancelar: () => void;
};

const VACIO = { codigo: "", identificacion: "", nombres: "", correo: "", carrera: "", clave: "" };

export default function FormUsuario({ onGuardado, onCancelar }: Props) {
  const [datos, setDatos] = useState(VACIO);
  const [rol, setRol] = useState<RolUsuario>("estudiante");
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [guardando, setGuardando] = useState(false);

  const cambiar = (campo: keyof typeof VACIO) => (e: { target: { value: string } }) =>
    setDatos((d) => ({ ...d, [campo]: e.target.value }));

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErrorGeneral("");
    const locales: Record<string, string> = {};
    if (!datos.codigo.trim()) locales.codigo = "Escribe el código institucional.";
    if (!datos.identificacion.trim()) locales.identificacion = "Escribe el documento de identidad.";
    if (!datos.nombres.trim()) locales.nombres = "Escribe el nombre completo.";
    if (!datos.correo.trim()) locales.correo = "Escribe el correo.";
    if (datos.clave.length < 8) locales.clave = "La clave inicial debe tener al menos 8 caracteres.";
    setErrores(locales);
    if (Object.keys(locales).length) return;
    setGuardando(true);
    try {
      onGuardado(await usuariosApi.registrar({ ...datos, rol }));
    } catch (err) {
      setErrores(erroresDeCampo(err));
      setErrorGeneral(mensajeError(err));
    } finally {
      setGuardando(false);
    }
  }

  const error = (campo: string) =>
    errores[campo] ? <small className="error-campo" id={`err-us-${campo}`}>{errores[campo]}</small> : null;
  const inv = (campo: string) =>
    errores[campo] ? { "aria-invalid": true, "aria-describedby": `err-us-${campo}` } : {};

  return (
    <form onSubmit={onSubmit} noValidate>
      <div className="dialogo-cuerpo">
        {errorGeneral && <div className="alerta alerta--error" role="alert">{errorGeneral}</div>}

        <div className="campo">
          <label htmlFor="us-nombres">Nombre completo</label>
          <input id="us-nombres" value={datos.nombres} onChange={cambiar("nombres")} maxLength={120} required {...inv("nombres")} />
          {error("nombres")}
        </div>

        <div className="fila-campos">
          <div className="campo">
            <label htmlFor="us-codigo">Código</label>
            <input id="us-codigo" value={datos.codigo} onChange={cambiar("codigo")} maxLength={20} placeholder="Ej. 200212345" required {...inv("codigo")} />
            {error("codigo")}
          </div>
          <div className="campo">
            <label htmlFor="us-identificacion">Identificación</label>
            <input id="us-identificacion" value={datos.identificacion} onChange={cambiar("identificacion")} maxLength={20} required {...inv("identificacion")} />
            {error("identificacion")}
          </div>
        </div>

        <div className="campo">
          <label htmlFor="us-correo">Correo</label>
          <input id="us-correo" type="email" value={datos.correo} onChange={cambiar("correo")} maxLength={120} placeholder="nombre@uninorte.edu.co" required {...inv("correo")} />
          {error("correo")}
        </div>

        <div className="fila-campos">
          <div className="campo">
            <label htmlFor="us-rol">Tipo de usuario</label>
            <select id="us-rol" value={rol} onChange={(e) => setRol(e.target.value as RolUsuario)} {...inv("rol")}>
              <option value="estudiante">Estudiante (7 días, hasta 3 libros)</option>
              <option value="docente">Docente (15 días, hasta 5 libros)</option>
            </select>
            {error("rol")}
          </div>
          <div className="campo">
            <label htmlFor="us-carrera">Carrera <span className="texto-suave">(opcional)</span></label>
            <input id="us-carrera" value={datos.carrera} onChange={cambiar("carrera")} maxLength={100} {...inv("carrera")} />
            {error("carrera")}
          </div>
        </div>

        <div className="campo">
          <label htmlFor="us-clave">Clave inicial</label>
          <input id="us-clave" type="password" autoComplete="new-password" value={datos.clave} onChange={cambiar("clave")} minLength={8} maxLength={128} required {...inv("clave")} />
          {error("clave") ?? <small>Entrégasela al usuario; con ella inicia sesión. Mínimo 8 caracteres.</small>}
        </div>
      </div>

      <div className="dialogo-pie">
        <button type="button" className="btn btn--secundario" onClick={onCancelar}>Cancelar</button>
        <button type="submit" className="btn" disabled={guardando}>
          {guardando ? "Registrando…" : "Registrar usuario"}
        </button>
      </div>
    </form>
  );
}
