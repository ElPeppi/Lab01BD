from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone


class Configuracion(models.Model):
    clave = models.CharField(max_length=50, primary_key=True)
    valor = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "configuracion"


class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey("usuarios.Usuario", models.DO_NOTHING, db_column="id_usuario")
    ejemplar = models.ForeignKey("ejemplares.Ejemplar", models.DO_NOTHING, db_column="id_ejemplar")
    empleado = models.ForeignKey("usuarios.Empleado", models.DO_NOTHING, db_column="id_empleado",
                                 null=True, blank=True)
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_prestamo = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=12, default="solicitado")
    motivo_rechazo = models.CharField(max_length=255, null=True, blank=True)
    # ejemplar_abierto es una columna generada por MySQL: NO se declara aqui.

    class Meta:
        managed = False
        db_table = "prestamo"


class Devolucion(models.Model):
    id_devolucion = models.AutoField(primary_key=True)
    prestamo = models.OneToOneField(Prestamo, models.DO_NOTHING, db_column="id_prestamo")
    empleado = models.ForeignKey("usuarios.Empleado", models.DO_NOTHING, db_column="id_empleado")
    fecha_devolucion = models.DateTimeField(default=timezone.now)
    observaciones = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "devolucion"


class Multa(models.Model):
    id_multa = models.AutoField(primary_key=True)
    devolucion = models.OneToOneField(Devolucion, models.DO_NOTHING, db_column="id_devolucion")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "multa"