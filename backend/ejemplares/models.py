from django.db import models

# Create your models here.
from django.db import models


class Ejemplar(models.Model):
    id_ejemplar = models.AutoField(primary_key=True)
    codigo_barras = models.CharField(max_length=30, unique=True)
    ubicacion = models.CharField(max_length=60)
    estado = models.CharField(max_length=12, default="disponible")
    condicion = models.CharField(max_length=10, default="bueno")
    libro = models.ForeignKey("catalogo.Libro", models.DO_NOTHING, db_column="id_libro")
    eliminado = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "ejemplar"