from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import APIException
from ejemplares.models import Ejemplar
from prestamos.models import Configuracion, Devolucion, Multa, Prestamo

CLAVE_TARIFA = "tarifa_multa_dia"

class ReglaDevolucion(APIException):
    """Se viola una regla de negocio (préstamo no aprobado, 
    multa ya pagada, etc.)."""
    status_code = 409
    default_code = "regla_devolucion"

class ConfiguracionInvalida(APIException):
    status_code=500
    default_code="configuracion:_invalida"

def tarifa_multa_dia():
    """Valor de la multa por día de retraso, leído de la tabla configuracion."""
    try:
        return Decimal(Configuracion.objects.get(clave=CLAVE_TARIFA).valor)
    except Configuracion.DoesNotExist:
        raise ConfiguracionInvalida(f"Falta el parámetro '{CLAVE_TARIFA}' en configuracion.")
    except InvalidOperation:
        raise ConfiguracionInvalida(f"El parámetro '{CLAVE_TARIFA}' no es un número.")

def dias_de_retraso(prestamo, fecha_devolucion):
    """Días entre el vencimiento y el día de la devolución (0 si llegó a tiempo)."""
    dia_devolucion = timezone.localdate(fecha_devolucion)
    return max((dia_devolucion - prestamo.fecha_vencimiento).days, 0)

@transaction.atomic
def registrar_devolucion(prestamo, empleado, observaciones=None,
                         condicion=Ejemplar.CONDICION_BUENO):
    # bloquear el préstamo evita que dos empleados lo devuelvan a la vez
    prestamo = Prestamo.objects.select_for_update().get(pk=prestamo.pk)
    if prestamo.estado != Prestamo.APROBADO:
        raise ReglaDevolucion(
            f"Solo se puede devolver un préstamo aprobado; este está {prestamo.estado}."
        )
    ejemplar = Ejemplar.objects.select_for_update().get(pk=prestamo.ejemplar_id)

    ahora = timezone.now()
    devolucion = Devolucion.objects.create(
        prestamo=prestamo, empleado=empleado,
        fecha_devolucion=ahora, observaciones=observaciones or None,
    )

    # multa: solo si hubo retraso y la tarifa es mayor que 0 (la BD exige monto > 0)
    dias = dias_de_retraso(prestamo, ahora)
    if dias > 0:
        tarifa = tarifa_multa_dia()
        if tarifa > 0:
            Multa.objects.create(devolucion=devolucion, monto=tarifa * dias)

    prestamo.estado = Prestamo.DEVUELTO
    prestamo.save(update_fields=["estado"])

    ejemplar.estado = Ejemplar.ESTADO_DISPONIBLE
    ejemplar.condicion = condicion
    ejemplar.save(update_fields=["estado", "condicion"])
    return devolucion

@transaction.atomic
def pagar_multa(multa):
    multa = Multa.objects.select_for_update().get(pk=multa.pk)
    if multa.pagada:
        raise ReglaDevolucion("La multa ya está pagada.")
    multa.pagada = True
    multa.fecha_pago = timezone.localdate()
    multa.save(update_fields=["pagada", "fecha_pago"])
    return multa


