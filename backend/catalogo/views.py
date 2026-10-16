from django.shortcuts import render
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Autor, Categoria, Editorial, Libro
from .serializers import (
    AutorSerializer, CategoriaSerializer, EditorialSerializer, LibroSerializer,
)


class BorradoSeguroMixin:

    def destroy(self, request, *args, **kwargs):
        objeto = self.get_object()
        if self.esta_en_uso(objeto):
            return Response(
                {"detail": "No se puede eliminar: hay libros que lo usan."},
                status=status.HTTP_409_CONFLICT,
            )
        objeto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EditorialViewSet(BorradoSeguroMixin, viewsets.ModelViewSet):
    queryset = Editorial.objects.all().order_by("nombre")
    serializer_class = EditorialSerializer

    def esta_en_uso(self, editorial):
        return Libro.objects.filter(editorial=editorial).exists()


class CategoriaViewSet(BorradoSeguroMixin, viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer

    def esta_en_uso(self, categoria):
        return Libro.objects.filter(categoria=categoria).exists()


class AutorViewSet(BorradoSeguroMixin, viewsets.ModelViewSet):
    queryset = Autor.objects.all().order_by("nombre")
    serializer_class = AutorSerializer

    def esta_en_uso(self, autor):
        return autor.libros.exists()


class LibroViewSet(viewsets.ModelViewSet):
    """
    CRUD de libros + búsqueda
    """
    serializer_class = LibroSerializer

    def get_queryset(self):
        ejemplares_vivos = Q(ejemplar__eliminado=False)
        qs = (
            Libro.objects.filter(eliminado=False)
            .select_related("editorial", "categoria")
            .prefetch_related("autores")
            .annotate(
                ejemplares_total=Count("ejemplar", filter=ejemplares_vivos, distinct=True),
                ejemplares_disponibles=Count(
                    "ejemplar",
                    filter=ejemplares_vivos & Q(ejemplar__estado="disponible"),
                    distinct=True,
                ),
            )
            .order_by("titulo")
        )

        p = self.request.query_params
        if p.get("titulo"):
            qs = qs.filter(titulo__icontains=p["titulo"])
        if p.get("isbn"):
            qs = qs.filter(isbn__icontains=p["isbn"])
        if p.get("autor"):
            qs = qs.filter(autores__nombre__icontains=p["autor"]).distinct()
        if p.get("categoria"):
            c = p["categoria"]
            qs = qs.filter(categoria_id=c) if c.isdigit() else qs.filter(categoria__nombre__icontains=c)
        if p.get("disponible") == "true":
            qs = qs.filter(ejemplares_disponibles__gt=0)
        elif p.get("disponible") == "false":
            qs = qs.filter(ejemplares_disponibles=0)
        return qs

    def destroy(self, request, *args, **kwargs):
        # el libro se oculta pero su historial de préstamos se conserva
        libro = self.get_object()
        libro.eliminado = True
        libro.save(update_fields=["eliminado"])
        return Response(status=status.HTTP_204_NO_CONTENT)
