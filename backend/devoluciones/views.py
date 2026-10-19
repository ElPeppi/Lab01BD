from django.shortcuts import render

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from prestamos.models import Devolucion, Multa

from . import servicios
from .serializers import DevolucionEntradaSerializer, DevolucionSerializer, MultaSerializer



class DevolucionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
   
    serializer_class = DevolucionSerializer

    def get_queryset(self):
        qs = (
            Devolucion.objects
            .select_related("prestamo__usuario", "prestamo__ejemplar__libro", "empleado", "multa")
            .order_by("-fecha_devolucion")
        )
        p = self.request.query_params
        if p.get("usuario", "").isdigit():
            qs = qs.filter(prestamo__usuario_id=p["usuario"])
        if p.get("prestamo", "").isdigit():
            qs = qs.filter(prestamo_id=p["prestamo"])
        if p.get("con_multa") == "true":
            qs = qs.filter(multa__isnull=False)
        elif p.get("con_multa") == "false":
            qs = qs.filter(multa__isnull=True)
        return qs

    def create(self, request, *args, **kwargs):
        entrada = DevolucionEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        devolucion = servicios.registrar_devolucion(**entrada.validated_data)
        devolucion = self.get_queryset().get(pk=devolucion.pk)  # recarga con sus relaciones
        return Response(DevolucionSerializer(devolucion).data, status=status.HTTP_201_CREATED)


class MultaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Las multas solo se consultan y se pagan: las crea la devolución."""
    serializer_class = MultaSerializer

    def get_queryset(self):
        qs = (
            Multa.objects
            .select_related("devolucion__prestamo__usuario")
            .order_by("-id_multa")
        )
        p = self.request.query_params
        if p.get("pagada") == "true":
            qs = qs.filter(pagada=True)
        elif p.get("pagada") == "false":
            qs = qs.filter(pagada=False)
        if p.get("usuario", "").isdigit():
            qs = qs.filter(devolucion__prestamo__usuario_id=p["usuario"])
        return qs

    @action(detail=True, methods=["post"])
    def pagar(self, request, pk=None):
        multa = servicios.pagar_multa(self.get_object())
        multa = self.get_queryset().get(pk=multa.pk)
        return Response(MultaSerializer(multa).data)
