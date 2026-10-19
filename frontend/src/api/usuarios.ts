import api from "./client";

export type RolUsuario = "estudiante" | "docente";
export type EstadoUsuario = "activo" | "bloqueado";

// GET /api/usuarios/  (personal de la biblioteca)
export type Usuario = {
  id_usuario: number;
  codigo: string;
  identificacion: string;
  nombres: string;
  correo: string;
  rol: RolUsuario;
  carrera: string | null;
  estado: EstadoUsuario;
};

// POST /api/usuarios/  (datos mínimos; la clave es la inicial, el backend guarda solo el hash)
export type UsuarioEntrada = {
  codigo: string;
  identificacion: string;
  nombres: string;
  correo: string;
  rol: RolUsuario;
  carrera: string;
  clave: string;
};

// Registrar, editar, bloquear y eliminar: solo el administrador
export const usuariosApi = {
  listar: (q?: string) =>
    api.get<Usuario[]>("/api/usuarios/", { params: { q: q || undefined } }).then((r) => r.data),

  registrar: (datos: UsuarioEntrada) => api.post<Usuario>("/api/usuarios/", datos).then((r) => r.data),

  // PATCH: solo cambia lo que llega; sin clave, se conserva la anterior
  actualizar: (id: number, datos: Partial<UsuarioEntrada>) =>
    api.patch<Usuario>(`/api/usuarios/${id}/`, datos).then((r) => r.data),

  cambiarEstado: (id: number, estado: EstadoUsuario) =>
    api.patch<Usuario>(`/api/usuarios/${id}/`, { estado }).then((r) => r.data),

  // Borrado lógico: deja de aparecer y no puede iniciar sesión; su historial se conserva
  eliminar: (id: number) => api.delete(`/api/usuarios/${id}/`),
};
