"""
API JSON de ejemplares para el frontend (React), montada en /api/ejemplares/.
Usa DRF para compartir con el resto del backend la autenticación JWT, los permisos
y el formato de errores ({"detail": ...} o {"campo": ["..."]}).
Solo el personal de la biblioteca puede usarla.
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from prestamos.models import Prestamo
from usuarios.permissions import EsEmpleado

from .forms import EjemplarForm
from .models import Ejemplar
from .views import _calcular_resumen_estados


def _serializar(ej):
    return {
        "id_ejemplar": ej.id_ejemplar,
        "codigo_barras": ej.codigo_barras,
        "ubicacion": ej.ubicacion,
        "estado": ej.estado,
        "condicion": ej.condicion,
        "eliminado": bool(ej.eliminado),
        "id_libro": ej.libro_id,
        "libro_titulo": ej.libro.titulo if ej.libro_id else None,
        "libro_isbn": ej.libro.isbn if ej.libro_id else None,
    }


def _datos_formulario(payload, ej=None):
    """Arma los datos del EjemplarForm; en una edición parcial conserva lo que no llega."""
    return {
        "codigo_barras": payload.get("codigo_barras", ej.codigo_barras if ej else None),
        "libro": payload.get("id_libro") or payload.get("libro") or (ej.libro_id if ej else None),
        "ubicacion": payload.get("ubicacion", ej.ubicacion if ej else None),
        "estado": payload.get("estado", ej.estado if ej else Ejemplar.ESTADO_DISPONIBLE),
        "condicion": payload.get("condicion", ej.condicion if ej else Ejemplar.CONDICION_BUENO),
    }


@api_view(["GET", "POST"])
@permission_classes([EsEmpleado])
def lista(request):
    """GET: listar con filtros (?q=, ?estado=, ?id_libro=). POST: registrar un ejemplar."""
    if request.method == "GET":
        qs = Ejemplar.objects.select_related("libro").filter(eliminado=False)
        p = request.query_params
        if p.get("estado"):
            qs = qs.filter(estado=p["estado"])
        libro_id = p.get("id_libro") or p.get("libro")
        if libro_id and str(libro_id).isdigit():
            qs = qs.filter(libro_id=int(libro_id))
        if p.get("q"):
            q = p["q"]
            qs = qs.filter(Q(codigo_barras__icontains=q) | Q(ubicacion__icontains=q) | Q(libro__titulo__icontains=q))
        data = [_serializar(ej) for ej in qs.order_by("id_ejemplar")]
        return Response({"count": len(data), "results": data})

    form = EjemplarForm(_datos_formulario(request.data))
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    ej = form.save(commit=False)
    ej.eliminado = False
    ej.save()
    return Response(_serializar(ej), status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([EsEmpleado])
def detalle(request, pk):
    """Consultar, editar o dar de baja (borrado lógico) un ejemplar."""
    ej = get_object_or_404(Ejemplar.objects.select_related("libro"), pk=pk)

    if request.method == "GET":
        return Response(_serializar(ej))

    if request.method == "DELETE":
        # Ni prestado ni con una solicitud pendiente: dejaría un préstamo huérfano
        abierto = Prestamo.objects.filter(ejemplar=ej, estado__in=Prestamo.ESTADOS_ABIERTOS).exists()
        if ej.estado == Ejemplar.ESTADO_PRESTADO or abierto:
            return Response(
                {"detail": "No se puede dar de baja: el ejemplar está prestado o tiene una solicitud pendiente."},
                status=status.HTTP_409_CONFLICT,
            )
        ej.eliminado = True
        ej.save(update_fields=["eliminado"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    form = EjemplarForm(_datos_formulario(request.data, ej), instance=ej)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(_serializar(form.save()))


@api_view(["GET"])
@permission_classes([EsEmpleado])
def inventario(request):
    """
    Reporte de inventario por estado. Con ?solo_resumen=true devuelve solo los totales
    (lo que necesitan las tarjetas del front) sin la lista completa de ejemplares.
    """
    qs = Ejemplar.objects.filter(eliminado=False).select_related("libro")
    resumen = _calcular_resumen_estados(qs)
    if request.query_params.get("solo_resumen") == "true":
        return Response({"resumen_global": resumen})

    estado = request.query_params.get("estado")
    if estado in {Ejemplar.ESTADO_DISPONIBLE, Ejemplar.ESTADO_PRESTADO, Ejemplar.ESTADO_PERDIDO}:
        qs = qs.filter(estado=estado)
    return Response({
        "resumen_global": resumen,
        "filtro_estado": estado or "todos",
        "total_filtrado": qs.count(),
        "ejemplares": [_serializar(ej) for ej in qs.order_by("codigo_barras")],
    })
