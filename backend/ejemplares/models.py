from django.core.exceptions import ValidationError
from django.db import models


class Ejemplar(models.Model):
    ESTADO_DISPONIBLE = "disponible"
    ESTADO_PRESTADO = "prestado"
    ESTADO_PERDIDO = "perdido"

    ESTADO_CHOICES = [
        (ESTADO_DISPONIBLE, "Disponible"),
        (ESTADO_PRESTADO, "Prestado"),
        (ESTADO_PERDIDO, "Perdido"),
    ]

    CONDICION_BUENO = "bueno"
    CONDICION_DANADO = "danado"

    CONDICION_CHOICES = [
        (CONDICION_BUENO, "Bueno"),
        (CONDICION_DANADO, "Dañado"),
    ]

    id_ejemplar = models.AutoField(primary_key=True)
    codigo_barras = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Código de barras / ID único",
    )
    ubicacion = models.CharField(
        max_length=60,
        verbose_name="Ubicación física (Sala / Estante)",
    )
    estado = models.CharField(
        max_length=12,
        choices=ESTADO_CHOICES,
        default=ESTADO_DISPONIBLE,
        verbose_name="Estado",
    )
    condicion = models.CharField(
        max_length=10,
        choices=CONDICION_CHOICES,
        default=CONDICION_BUENO,
        verbose_name="Condición física",
    )
    libro = models.ForeignKey(
        "catalogo.Libro",
        models.DO_NOTHING,
        db_column="id_libro",
        verbose_name="Libro",
    )
    eliminado = models.BooleanField(default=False, verbose_name="Dado de baja")

    class Meta:
        managed = False
        db_table = "ejemplar"
        verbose_name = "Ejemplar físico"
        verbose_name_plural = "Ejemplares físicos"

    def __str__(self):
        titulo = getattr(self.libro, "titulo", f"Libro #{self.libro_id}")
        return f"[{self.codigo_barras}] {titulo} ({self.get_estado_display()})"

    @property
    def esta_disponible(self):
        return not self.eliminado and self.estado == self.ESTADO_DISPONIBLE

    def clean(self):
        super().clean()
        if self.codigo_barras:
            self.codigo_barras = self.codigo_barras.strip()
        if self.ubicacion:
            self.ubicacion = self.ubicacion.strip()
        estados_validos = {c[0] for c in self.ESTADO_CHOICES}
        if self.estado not in estados_validos:
            raise ValidationError({"estado": "El estado debe ser disponible, prestado o perdido."})
        condiciones_validas = {c[0] for c in self.CONDICION_CHOICES}
        if self.condicion not in condiciones_validas:
            raise ValidationError({"condicion": "La condición debe ser bueno o danado."})