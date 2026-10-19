from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Empleado, PoliticaPrestamo, Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Registro de usuarios con los datos mínimos: código, identificación, nombres,
    correo, rol y una clave inicial. La carrera es opcional.
    La clave nunca se devuelve; en la BD solo queda su hash.
    """
    rol = serializers.SlugRelatedField(slug_field="rol", queryset=PoliticaPrestamo.objects.all())
    clave = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = Usuario
        fields = [
            "id_usuario", "codigo", "identificacion", "nombres", "correo",
            "rol", "carrera", "estado", "clave",
        ]
        read_only_fields = ["id_usuario", "estado"]
        # Mensajes propios en español (abajo) en vez de los UniqueValidator por defecto
        extra_kwargs = {
            "codigo": {"validators": []},
            "identificacion": {"validators": []},
            "correo": {"validators": []},
        }

    def _unico(self, campo, valor, texto):
        valor = valor.strip()
        if Usuario.objects.filter(**{campo: valor}).exists():
            raise serializers.ValidationError(f"Ya existe un usuario con {texto}.")
        return valor

    def validate_codigo(self, valor):
        return self._unico("codigo", valor, "ese código")

    def validate_identificacion(self, valor):
        return self._unico("identificacion", valor, "esa identificación")

    def validate_correo(self, valor):
        valor = serializers.EmailField().run_validation(valor.strip().lower())
        # El login busca primero en empleado: un correo repetido dejaría la cuenta inaccesible
        if Empleado.objects.filter(correo=valor).exists():
            raise serializers.ValidationError("Ese correo pertenece a un empleado.")
        return self._unico("correo", valor, "ese correo")

    def validate_nombres(self, valor):
        return valor.strip()

    def validate_carrera(self, valor):
        return (valor or "").strip() or None

    def create(self, datos):
        datos["clave_hash"] = make_password(datos.pop("clave"))
        return Usuario.objects.create(**datos)
