from django.db import models

# Create your models here.
from django.db import models


class PoliticaPrestamo(models.Model):
    rol = models.CharField(max_length=20, primary_key=True)
    dias_prestamo = models.IntegerField()
    max_prestamos = models.IntegerField()

    class Meta:
        managed = False
        db_table = "politica_prestamo"


class Usuario(models.Model):
    ESTADO_ACTIVO = "activo"
    ESTADO_BLOQUEADO = "bloqueado"

    ESTADO_CHOICES = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_BLOQUEADO, "Bloqueado"),
    ]

    id_usuario = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    identificacion = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=120)
    correo = models.CharField(max_length=120, unique=True)
    clave_hash = models.CharField(max_length=255)
    rol = models.ForeignKey(PoliticaPrestamo, models.DO_NOTHING, db_column="rol")
    carrera = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default=ESTADO_ACTIVO)
    eliminado = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "usuario"


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=120)
    correo = models.CharField(max_length=120, unique=True)
    clave_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, default="bibliotecario")

    class Meta:
        managed = False
        db_table = "empleado"