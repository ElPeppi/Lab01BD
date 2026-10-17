import datetime as dt
import jwt
from django.conf import settings

ALGORITMO = "HS256"
ACCESS_DURACION = dt.timedelta(minutes=30)
REFRESH_DURACION = dt.timedelta(days=1)


def _firmar(base, duracion, tipo):
    ahora = dt.datetime.now(dt.timezone.utc)
    datos = {**base, "tipo": tipo, "iat": ahora, "exp": ahora + duracion}
    return jwt.encode(datos, settings.SECRET_KEY, algorithm=ALGORITMO)


def crear_tokens(sujeto, id_, rol, nombre):
    """sujeto = 'empleado' o 'usuario' (son tablas distintas)."""
    base = {"sub": f"{sujeto}:{id_}", "rol": rol, "nombre": nombre}
    return {
        "access": _firmar(base, ACCESS_DURACION, "access"),
        "refresh": _firmar(base, REFRESH_DURACION, "refresh"),
    }


def decodificar(token, tipo_esperado):
    datos = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITMO])
    if datos.get("tipo") != tipo_esperado:
        raise jwt.InvalidTokenError("Tipo de token incorrecto")
    return datos