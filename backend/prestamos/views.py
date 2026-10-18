from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import servicios
from .models import Prestamo
from .serializers import (
    AprobacionSerializer, PrestamoSerializer, RechazoSerializer, SolicitudSerializer,
)


class PrestamoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    Listado/consulta de préstamos + solicitud, aprobación y rechazo.
    No hay PUT/DELETE: el préstamo solo cambia de estado por sus acciones.
    """
    serializer_class = PrestamoSerializer

    def get_queryset(self):
        qs = (
            Prestamo.objects
            .select_related("usuario", "ejemplar__libro", "empleado")
            .order_by("-fecha_solicitud")
        )

        p = self.request.query_params
        if p.get("estado"):
            qs = qs.filter(estado=p["estado"])
        if p.get("usuario", "").isdigit():
            qs = qs.filter(usuario_id=p["usuario"])
        if p.get("ejemplar", "").isdigit():
            qs = qs.filter(ejemplar_id=p["ejemplar"])
        if p.get("libro", "").isdigit():
            qs = qs.filter(ejemplar__libro_id=p["libro"])
        if p.get("activos") == "true":
            qs = qs.filter(estado=Prestamo.APROBADO)
        if p.get("vencidos") == "true":
            qs = qs.filter(estado=Prestamo.APROBADO, fecha_vencimiento__lt=timezone.localdate())
        return qs

    def _respuesta(self, prestamo, codigo=status.HTTP_200_OK):
        prestamo = Prestamo.objects.select_related(
            "usuario", "ejemplar__libro", "empleado"
        ).get(pk=prestamo.pk)
        return Response(PrestamoSerializer(prestamo).data, status=codigo)

    def create(self, request, *args, **kwargs):
        entrada = SolicitudSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        prestamo = servicios.solicitar_prestamo(**entrada.validated_data)
        return self._respuesta(prestamo, status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        entrada = AprobacionSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        prestamo = servicios.aprobar_prestamo(self.get_object(), **entrada.validated_data)
        return self._respuesta(prestamo)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        entrada = RechazoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        prestamo = servicios.rechazar_prestamo(self.get_object(), **entrada.validated_data)
        return self._respuesta(prestamo)
