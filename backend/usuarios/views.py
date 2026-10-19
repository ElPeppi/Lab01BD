import jwt
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .jwt_utils import crear_tokens, decodificar
from .models import Empleado, Usuario
from .permissions import EsAdmin, EsEmpleado
from .serializers import UsuarioSerializer


def _perfil(tipo, id_, nombre, rol):
    return {"tipo": tipo, "id": id_, "nombre": nombre, "rol": rol}


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    correo = (request.data.get("correo") or "").strip()
    clave = request.data.get("clave") or ""
    if not correo or not clave:
        return Response({"error": "Correo y contraseña son obligatorios."}, status=400)

    emp = Empleado.objects.filter(correo=correo).first()
    if emp and check_password(clave, emp.clave_hash):
        return Response({
            **crear_tokens("empleado", emp.id_empleado, emp.rol, emp.nombres),
            "perfil": _perfil("empleado", emp.id_empleado, emp.nombres, emp.rol),
        })

    usr = Usuario.objects.filter(correo=correo, eliminado=False).first()
    if usr and check_password(clave, usr.clave_hash):
        if usr.estado != "activo":
            return Response({"error": "Tu cuenta está bloqueada. Acércate a la biblioteca."}, status=403)
        return Response({
            **crear_tokens("usuario", usr.id_usuario, usr.rol_id, usr.nombres),
            "perfil": _perfil("usuario", usr.id_usuario, usr.nombres, usr.rol_id),
        })

    return Response({"error": "Correo o contraseña incorrectos."}, status=401)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def refresh(request):
    token = request.data.get("refresh")
    if not token:
        return Response({"error": "Falta el refresh token."}, status=400)
    try:
        datos = decodificar(token, "refresh")
    except jwt.ExpiredSignatureError:
        return Response({"error": "Sesión expirada, inicia sesión de nuevo."}, status=401)
    except jwt.InvalidTokenError:
        return Response({"error": "Token inválido."}, status=401)

    tipo, id_ = datos["sub"].split(":")
    if tipo == "empleado":
        emp = Empleado.objects.filter(id_empleado=id_).first()
        if not emp:
            return Response({"error": "Cuenta no encontrada."}, status=401)
        return Response(crear_tokens("empleado", emp.id_empleado, emp.rol, emp.nombres))

    usr = Usuario.objects.filter(id_usuario=id_, eliminado=False, estado="activo").first()
    if not usr:
        return Response({"error": "Cuenta bloqueada o eliminada."}, status=401)
    return Response(crear_tokens("usuario", usr.id_usuario, usr.rol_id, usr.nombres))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    return Response(_perfil(u.tipo, u.id, u.nombre, u.rol))

class UsuarioViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Listado y registro de usuarios (estudiantes y docentes).
    Consultar: todo el personal (para buscar a la persona y ver su historial de préstamos).
    Registrar: solo el administrador.
    """
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        return [EsAdmin()] if self.action == "create" else [EsEmpleado()]

    def get_queryset(self):
        qs = Usuario.objects.filter(eliminado=False).order_by("nombres")
        q = self.request.query_params.get("q", "").strip()
        if q:
            qs = qs.filter(Q(nombres__icontains=q) | Q(codigo__icontains=q) | Q(correo__icontains=q))
        return qs

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            # Dos registros simultáneos con el mismo código/correo: lo frena el UNIQUE de MySQL
            raise ValidationError({"detail": "Ya existe un usuario con ese código, identificación o correo."})
