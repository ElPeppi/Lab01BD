from rest_framework import serializers

from catalogo.models import Libro
from ejemplares.models import Ejemplar
from usuarios.models import Empleado, Usuario

from .models import Prestamo


class PrestamoSerializer(serializers.ModelSerializer):
    # Solo lectura: los cambios de estado se hacen con solicitar/aprobar/rechazar.
    usuario_nombres = serializers.CharField(source="usuario.nombres", read_only=True)
    usuario_codigo = serializers.CharField(source="usuario.codigo", read_only=True)
    ejemplar_codigo = serializers.CharField(source="ejemplar.codigo_barras", read_only=True)
    libro = serializers.IntegerField(source="ejemplar.libro_id", read_only=True)
    libro_titulo = serializers.CharField(source="ejemplar.libro.titulo", read_only=True)
    empleado_nombres = serializers.CharField(
        source="empleado.nombres", read_only=True, default=None
    )
    vencido = serializers.BooleanField(read_only=True)
    dias_retraso = serializers.IntegerField(read_only=True)

    class Meta:
        model = Prestamo
        fields = [
            "id_prestamo", "estado",
            "usuario", "usuario_nombres", "usuario_codigo",
            "ejemplar", "ejemplar_codigo", "libro", "libro_titulo",
            "empleado", "empleado_nombres",
            "fecha_solicitud", "fecha_aprobacion",
            "fecha_prestamo", "fecha_vencimiento",
            "motivo_rechazo", "vencido", "dias_retraso",
        ]
        read_only_fields = fields


class SolicitudSerializer(serializers.Serializer):
    """El usuario pide un libro (se le asigna un ejemplar libre) o un ejemplar concreto."""
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    libro = serializers.PrimaryKeyRelatedField(queryset=Libro.objects.all(), required=False)
    ejemplar = serializers.PrimaryKeyRelatedField(queryset=Ejemplar.objects.all(), required=False)

    def validate(self, data):
        if ("libro" in data) == ("ejemplar" in data):
            raise serializers.ValidationError("Indique el libro o el ejemplar, solo uno de los dos.")
        return data


class AprobacionSerializer(serializers.Serializer):
    # Sin fechas se presta hoy y vence según la política del rol del usuario.
    empleado = serializers.PrimaryKeyRelatedField(queryset=Empleado.objects.all())
    fecha_prestamo = serializers.DateField(required=False)
    fecha_vencimiento = serializers.DateField(required=False)


class RechazoSerializer(serializers.Serializer):
    empleado = serializers.PrimaryKeyRelatedField(queryset=Empleado.objects.all())
    motivo_rechazo = serializers.CharField(max_length=255)
