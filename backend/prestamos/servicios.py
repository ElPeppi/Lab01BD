"""
Reglas de negocio del préstamo: solicitud (usuario) -> aprobación o rechazo (empleado).
La devolución pertenece al módulo de devoluciones.
"""
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import APIException

from ejemplares.models import Ejemplar
from usuarios.models import Usuario

from .models import Prestamo


class ReglaPrestamo(APIException):
    """Se viola una regla de negocio (usuario bloqueado, ejemplar ocupado, etc.)."""
    status_code = 409
    default_code = "regla_prestamo"


def _validar_usuario_activo(usuario):
    if usuario.eliminado or usuario.estado != "activo":
        raise ReglaPrestamo("El usuario no está activo; no puede tener préstamos.")


def _validar_cupo(usuario):
    abiertos = Prestamo.objects.filter(
        usuario=usuario, estado__in=Prestamo.ESTADOS_ABIERTOS
    ).count()
    if abiertos >= usuario.rol.max_prestamos:
        raise ReglaPrestamo(
            f"El usuario alcanzó el máximo de {usuario.rol.max_prestamos} préstamos "
            f"para el rol {usuario.rol_id}."
        )


def _ejemplares_libres():
    abierto = Prestamo.objects.filter(
        ejemplar=OuterRef("pk"), estado__in=Prestamo.ESTADOS_ABIERTOS
    )
    return Ejemplar.objects.filter(
        eliminado=False,
        estado=Ejemplar.ESTADO_DISPONIBLE,
        libro__eliminado=False,
    ).exclude(Exists(abierto))


@transaction.atomic
def solicitar_prestamo(usuario, libro=None, ejemplar=None):
    # bloquear al usuario serializa sus solicitudes y evita pasarse del cupo
    usuario = Usuario.objects.select_for_update().select_related("rol").get(pk=usuario.pk)
    _validar_usuario_activo(usuario)
    _validar_cupo(usuario)

    if ejemplar is None:
        if libro.eliminado:
            raise ReglaPrestamo("El libro no está en el catálogo.")
        # "bueno" < "danado": se prefieren los ejemplares en buen estado
        ejemplar = (
            _ejemplares_libres().filter(libro=libro)
            .order_by("condicion", "id_ejemplar").first()
        )
        if ejemplar is None:
            raise ReglaPrestamo("No hay ejemplares disponibles de este libro.")
    elif not _ejemplares_libres().filter(pk=ejemplar.pk).exists():
        raise ReglaPrestamo("El ejemplar no está disponible.")

    try:
        with transaction.atomic():
            return Prestamo.objects.create(usuario=usuario, ejemplar=ejemplar)
    except IntegrityError:
        # uq_ejemplar_abierto: otra solicitud tomó el ejemplar al mismo tiempo
        raise ReglaPrestamo("El ejemplar ya tiene un préstamo en curso.")


def _bloquear_solicitud(prestamo):
    prestamo = (
        Prestamo.objects.select_for_update()
        .select_related("usuario__rol")
        .get(pk=prestamo.pk)
    )
    if prestamo.estado != Prestamo.SOLICITADO:
        raise ReglaPrestamo(f"El préstamo ya está {prestamo.estado}.")
    return prestamo


@transaction.atomic
def aprobar_prestamo(prestamo, empleado, fecha_prestamo=None, fecha_vencimiento=None):
    prestamo = _bloquear_solicitud(prestamo)
    ejemplar = Ejemplar.objects.select_for_update().get(pk=prestamo.ejemplar_id)

    # se valida de nuevo: el usuario o el ejemplar pudieron cambiar desde la solicitud
    _validar_usuario_activo(prestamo.usuario)
    if ejemplar.eliminado or ejemplar.estado != Ejemplar.ESTADO_DISPONIBLE:
        raise ReglaPrestamo("El ejemplar ya no está disponible.")

    fecha_prestamo = fecha_prestamo or timezone.localdate()
    fecha_vencimiento = fecha_vencimiento or (
        fecha_prestamo + timedelta(days=prestamo.usuario.rol.dias_prestamo)
    )
    if fecha_vencimiento <= fecha_prestamo:
        raise serializers.ValidationError(
            {"fecha_vencimiento": "Debe ser posterior a la fecha de préstamo."}
        )

    prestamo.estado = Prestamo.APROBADO
    prestamo.empleado = empleado
    prestamo.fecha_aprobacion = timezone.now()
    prestamo.fecha_prestamo = fecha_prestamo
    prestamo.fecha_vencimiento = fecha_vencimiento
    prestamo.save(update_fields=[
        "estado", "empleado", "fecha_aprobacion", "fecha_prestamo", "fecha_vencimiento",
    ])

    ejemplar.estado = Ejemplar.ESTADO_PRESTADO
    ejemplar.save(update_fields=["estado"])
    return prestamo


@transaction.atomic
def rechazar_prestamo(prestamo, empleado, motivo_rechazo):
    prestamo = _bloquear_solicitud(prestamo)
    prestamo.estado = Prestamo.RECHAZADO
    prestamo.empleado = empleado
    prestamo.motivo_rechazo = motivo_rechazo
    prestamo.save(update_fields=["estado", "empleado", "motivo_rechazo"])
    return prestamo
