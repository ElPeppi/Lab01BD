import api from "./client";

export type RolUsuario = "estudiante" | "docente";

// GET /api/usuarios/  (solo admin)
export type Usuario = {
  id_usuario: number;
  codigo: string;
  identificacion: string;
  nombres: string;
  correo: string;
  rol: RolUsuario;
  carrera: string | null;
  estado: "activo" | "bloqueado";
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

export const usuariosApi = {
  listar: (q?: string) =>
    api.get<Usuario[]>("/api/usuarios/", { params: { q: q || undefined } }).then((r) => r.data),

  registrar: (datos: UsuarioEntrada) => api.post<Usuario>("/api/usuarios/", datos).then((r) => r.data),
};
