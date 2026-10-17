from django import forms
from django.core.exceptions import ValidationError

from catalogo.models import Categoria, Libro
from .models import Ejemplar


class LibroChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.titulo} (ISBN: {obj.isbn})"


class LibroFiltroChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.titulo


class CategoriaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre


class EjemplarForm(forms.ModelForm):
    libro = LibroChoiceField(
        queryset=Libro.objects.none(),
        label="Libro asociado",
        empty_label="Seleccione un libro del catálogo...",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Ejemplar
        fields = ["codigo_barras", "libro", "ubicacion", "estado", "condicion"]
        widgets = {
            "codigo_barras": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej. BC-0001 o ISBN-EJ-01",
                    "maxlength": "30",
                }
            ),
            "ubicacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej. Sala General - Estante A1",
                    "maxlength": "60",
                }
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "condicion": forms.Select(attrs={"class": "form-select"}),
        }

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

    def clean_ubicacion(self):
        ubicacion = (self.cleaned_data.get("ubicacion") or "").strip()
        if not ubicacion:
            raise ValidationError("La ubicación física (sala/estante) es obligatoria.")
        return ubicacion


class FiltroEjemplarForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Código, título, autor, ISBN o ubicación...",
            }
        ),
    )
    libro = LibroFiltroChoiceField(
        queryset=Libro.objects.none(),
        required=False,
        empty_label="Todos los libros",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    categoria = CategoriaChoiceField(
        queryset=Categoria.objects.none(),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    estado = forms.ChoiceField(
        choices=[("", "Todos los estados")] + Ejemplar.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    condicion = forms.ChoiceField(
        choices=[("", "Todas las condiciones")] + Ejemplar.CONDICION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    mostrar_bajas = forms.BooleanField(
        required=False,
        label="Incluir dados de baja",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["libro"].queryset = Libro.objects.filter(eliminado=False).order_by("titulo")
        self.fields["categoria"].queryset = Categoria.objects.all().order_by("nombre")
