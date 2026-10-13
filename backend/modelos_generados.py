# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Autor(models.Model):
    id_autor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = 'autor'


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'categoria'


class Configuracion(models.Model):
    clave = models.CharField(primary_key=True, max_length=50)
    valor = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'configuracion'


class Devolucion(models.Model):
    id_devolucion = models.AutoField(primary_key=True)
    id_prestamo = models.OneToOneField('Prestamo', models.DO_NOTHING, db_column='id_prestamo')
    id_empleado = models.ForeignKey('Empleado', models.DO_NOTHING, db_column='id_empleado')
    fecha_devolucion = models.DateTimeField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'devolucion'


class Editorial(models.Model):
    id_editorial = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'editorial'


class Ejemplar(models.Model):
    id_ejemplar = models.AutoField(primary_key=True)
    codigo_barras = models.CharField(unique=True, max_length=30)
    ubicacion = models.CharField(max_length=60)
    estado = models.CharField(max_length=12)
    condicion = models.CharField(max_length=10)
    id_libro = models.ForeignKey('Libro', models.DO_NOTHING, db_column='id_libro')
    eliminado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ejemplar'


class Empleado(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=120)
    correo = models.CharField(unique=True, max_length=120)
    clave_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'empleado'


class Libro(models.Model):
    id_libro = models.AutoField(primary_key=True)
    isbn = models.CharField(unique=True, max_length=17)
    titulo = models.CharField(max_length=200)
    anio = models.SmallIntegerField()
    descripcion = models.TextField(blank=True, null=True)
    id_editorial = models.ForeignKey(Editorial, models.DO_NOTHING, db_column='id_editorial')
    id_categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column='id_categoria')
    eliminado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'libro'


class LibroAutor(models.Model):
    pk = models.CompositePrimaryKey('id_libro', 'id_autor')
    id_libro = models.ForeignKey(Libro, models.DB_CASCADE, db_column='id_libro')
    id_autor = models.ForeignKey(Autor, models.DO_NOTHING, db_column='id_autor')

    class Meta:
        managed = False
        db_table = 'libro_autor'


class Multa(models.Model):
    id_multa = models.AutoField(primary_key=True)
    id_devolucion = models.OneToOneField(Devolucion, models.DO_NOTHING, db_column='id_devolucion')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagada = models.IntegerField()
    fecha_pago = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'multa'


class PoliticaPrestamo(models.Model):
    rol = models.CharField(primary_key=True, max_length=20)
    dias_prestamo = models.IntegerField()
    max_prestamos = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'politica_prestamo'


class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario')
    id_ejemplar = models.ForeignKey(Ejemplar, models.DO_NOTHING, db_column='id_ejemplar')
    id_empleado = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='id_empleado', blank=True, null=True)
    fecha_solicitud = models.DateTimeField()
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    fecha_prestamo = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=12)
    motivo_rechazo = models.CharField(max_length=255, blank=True, null=True)
    ejemplar_abierto = models.IntegerField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prestamo'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    codigo = models.CharField(unique=True, max_length=20)
    identificacion = models.CharField(unique=True, max_length=20)
    nombres = models.CharField(max_length=120)
    correo = models.CharField(unique=True, max_length=120)
    clave_hash = models.CharField(max_length=255)
    rol = models.ForeignKey(PoliticaPrestamo, models.DO_NOTHING, db_column='rol')
    carrera = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=10)
    eliminado = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'usuario'
