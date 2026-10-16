from django.db import models


class Editorial(models.Model):
    id_editorial = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = "editorial"


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        managed = False
        db_table = "categoria"


class Autor(models.Model):
    id_autor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = "autor"


class Libro(models.Model):
    id_libro = models.AutoField(primary_key=True)
    isbn = models.CharField(max_length=17, unique=True)
    titulo = models.CharField(max_length=200)
    anio = models.SmallIntegerField()
    descripcion = models.TextField(null=True, blank=True)
    editorial = models.ForeignKey(Editorial, models.DO_NOTHING, db_column="id_editorial")
    categoria = models.ForeignKey(Categoria, models.DO_NOTHING, db_column="id_categoria")
    eliminado = models.BooleanField(default=False)
    autores = models.ManyToManyField(Autor, through="LibroAutor", related_name="libros")

    class Meta:
        managed = False
        db_table = "libro"


class LibroAutor(models.Model):
    pk = models.CompositePrimaryKey("libro_id", "autor_id")
    libro = models.ForeignKey(Libro, models.DO_NOTHING, db_column="id_libro")
    autor = models.ForeignKey(Autor, models.DO_NOTHING, db_column="id_autor")

    class Meta:
        managed = False
        db_table = "libro_autor"