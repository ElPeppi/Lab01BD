from django.db import transaction
from rest_framework import serializers

from .models import Autor, Categoria, Editorial, Libro, LibroAutor


class EditorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editorial
        fields = ["id_editorial", "nombre"]


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id_categoria", "nombre"]


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ["id_autor", "nombre"]


class LibroSerializer(serializers.ModelSerializer):
    # Para escribir se mandan los ids; para leer se devuelven los datos completos.
    editorial = serializers.PrimaryKeyRelatedField(queryset=Editorial.objects.all())
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    autores = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(), many=True, write_only=True
    )


    editorial_nombre = serializers.CharField(source="editorial.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    autores_detalle = AutorSerializer(source="autores", many=True, read_only=True)
    ejemplares_disponibles = serializers.IntegerField(read_only=True)
    ejemplares_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Libro
        fields = [
            "id_libro", "isbn", "titulo", "anio", "descripcion",
            "editorial", "editorial_nombre",
            "categoria", "categoria_nombre",
            "autores", "autores_detalle",
            "ejemplares_disponibles", "ejemplares_total",
        ]

    def validate_anio(self, value):
        if not 1400 <= value <= 2100:
            raise serializers.ValidationError("El año debe estar entre 1400 y 2100.")
        return value

    def validate_autores(self, value):
        if not value:
            raise serializers.ValidationError("El libro debe tener al menos un autor.")
        return value

    def _guardar_autores(self, libro, autores):
        LibroAutor.objects.filter(libro=libro).delete()
        LibroAutor.objects.bulk_create(
            [LibroAutor(libro=libro, autor=autor) for autor in autores]
        )


    @transaction.atomic
    def create(self, validated_data):
        autores = validated_data.pop("autores")
        libro = Libro.objects.create(**validated_data)
        self._guardar_autores(libro, autores)
        return libro

    @transaction.atomic
    def update(self, instance, validated_data):
        autores = validated_data.pop("autores", None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()
        if autores is not None:
            self._guardar_autores(instance, autores)
        return instance