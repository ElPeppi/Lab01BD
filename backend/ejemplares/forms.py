from django import forms
from django.core.exceptions import ValidationError

from catalogo.models import Libro
from .models import Ejemplar


class EjemplarForm(forms.ModelForm):
    """Valida los datos de un ejemplar para la API (/api/ejemplares/)."""
    libro = forms.ModelChoiceField(queryset=Libro.objects.none())

    class Meta:
        model = Ejemplar
        fields = ["codigo_barras", "libro", "ubicacion", "estado", "condicion"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["libro"].queryset = Libro.objects.filter(eliminado=False).order_by("titulo")

    def clean_codigo_barras(self):
        codigo = (self.cleaned_data.get("codigo_barras") or "").strip().upper()
        if not codigo:
            raise ValidationError("El código de barras es obligatorio.")
        qs = Ejemplar.objects.filter(codigo_barras__iexact=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un ejemplar registrado con este código de barras.")
        return codigo

    def clean_estado(self):
        # "prestado" es consecuencia de un préstamo aprobado: no se pone ni se quita a mano
        nuevo = self.cleaned_data.get("estado")
        actual = self.instance.estado if self.instance and self.instance.pk else None
        if nuevo == Ejemplar.ESTADO_PRESTADO and actual != Ejemplar.ESTADO_PRESTADO:
            raise ValidationError("El estado prestado lo asigna el sistema al aprobar un préstamo.")
        if actual == Ejemplar.ESTADO_PRESTADO and nuevo != Ejemplar.ESTADO_PRESTADO:
            raise ValidationError("Este ejemplar está prestado: cambia de estado al registrar la devolución.")
        return nuevo

    def clean_ubicacion(self):
        ubicacion = (self.cleaned_data.get("ubicacion") or "").strip()
        if not ubicacion:
            raise ValidationError("La ubicación física (sala/estante) es obligatoria.")
        return ubicacion
