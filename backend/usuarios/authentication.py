from dataclasses import dataclass
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_utils import decodificar


@dataclass
class UsuarioToken:
    tipo: str      # 'empleado' | 'usuario'
    id: int
    rol: str       # 'admin' | 'bibliotecario' | 'estudiante' | 'docente'
    nombre: str
    is_authenticated: bool = True


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None  # sin token = anónimo; los permisos deciden
        try:
            datos = decodificar(header.split(" ", 1)[1], "access")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token inválido")
        tipo, id_ = datos["sub"].split(":")
        return UsuarioToken(tipo, int(id_), datos["rol"], datos["nombre"]), datos

    def authenticate_header(self, request):
        return "Bearer"  # hace que DRF responda 401 (no 403), que es lo que espera el client.ts