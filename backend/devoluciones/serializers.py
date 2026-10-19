from rest_framework import serializers

from ejemplares.models import Ejemplar
from prestamos.models import Devolucion, Multa, Prestamo
from usuarios.models import Empleado

from .servicios import dias_de_retraso


class DevolucionEntradaSerializer(serializers.Serializer):
    """Lo que manda el frontend para registrar una devolución."""
    prestamo = serializers.PrimaryKeyRelatedField(queryset=Prestamo.objects.all())
    empleado = serializers.PrimaryKeyRelatedField(queryset=Empleado.objects.all())
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True)
    # en qué estado vuelve el ejemplar
    condicion = serializers.ChoiceField(
        choices=Ejemplar.CONDICION_CHOICES, default=Ejemplar.CONDICION_BUENO
    )


class MultaSerializer(serializers.ModelSerializer):
    # Solo lectura: las multas las crea la devolución y solo cambian al pagarse.
    prestamo = serializers.IntegerField(source="devolucion.prestamo_id", read_only=True)
    usuario = serializers.IntegerField(source="devolucion.prestamo.usuario_id", read_only=True)
    usuario_nombres = serializers.CharField(
        source="devolucion.prestamo.usuario.nombres", read_only=True
    )

    class Meta:
        model = Multa
        fields = [
            "id_multa", "devolucion", "prestamo", "usuario", "usuario_nombres",
            "monto", "pagada", "fecha_pago",
        ]
        read_only_fields = fields


class DevolucionSerializer(serializers.ModelSerializer):
    usuario = serializers.IntegerField(source="prestamo.usuario_id", read_only=True)
    usuario_nombres = serializers.CharField(source="prestamo.usuario.nombres", read_only=True)
    ejemplar = serializers.IntegerField(source="prestamo.ejemplar_id", read_only=True)
    libro_titulo = serializers.CharField(source="prestamo.ejemplar.libro.titulo", read_only=True)
    empleado_nombres = serializers.CharField(source="empleado.nombres", read_only=True)
    fecha_vencimiento = serializers.DateField(source="prestamo.fecha_vencimiento", read_only=True)
    dias_retraso = serializers.SerializerMethodField()
    multa = serializers.SerializerMethodField()

    class Meta:
        model = Devolucion
        fields = [
            "id_devolucion", "prestamo", "usuario", "usuario_nombres",
            "ejemplar", "libro_titulo", "empleado", "empleado_nombres",
            "fecha_vencimiento", "fecha_devolucion", "dias_retraso",
            "observaciones", "multa",
        ]
        read_only_fields = fields

    def get_dias_retraso(self, obj):
        return dias_de_retraso(obj.prestamo, obj.fecha_devolucion)

    def get_multa(self, obj):
        multa = getattr(obj, "multa", None)  # None si no hubo retraso
        if multa is None:
            return None
        return {"id_multa": multa.id_multa, "monto": str(multa.monto), "pagada": multa.pagada}