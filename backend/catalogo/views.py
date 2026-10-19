from django.db.models import Count, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from rest_framework import status, viewsets
from rest_framework.response import Response

from prestamos.servicios import ejemplares_libres
from usuarios.permissions import SoloLecturaOEmpleado

from .models import Autor, Categoria, Editorial, Libro
from .serializers import (
    AutorSerializer, CategoriaSerializer, EditorialSerializer, LibroSerializer,
)


class BorradoSeguroMixin:
    # Consultar: cualquier sesión. Crear/editar/borrar: solo personal.
    permission_classes = [SoloLecturaOEmpleado]

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
    permission_classes = [SoloLecturaOEmpleado]

    def get_queryset(self):
        ejemplares_vivos = Q(ejemplar__eliminado=False)
        # "Disponibles" = los que se pueden prestar ya: misma regla que usa la solicitud
        # de préstamo (excluye los que tienen una solicitud pendiente), así el número que
        # ve el usuario coincide con lo que el backend le va a dejar pedir.
        libres = (
            ejemplares_libres().filter(libro=OuterRef("pk"))
            .order_by().values("libro").annotate(n=Count("pk")).values("n")
        )
        qs = (
            Libro.objects.filter(eliminado=False)
            .select_related("editorial", "categoria")
            .prefetch_related("autores")
            .annotate(
                ejemplares_total=Count("ejemplar", filter=ejemplares_vivos, distinct=True),
                ejemplares_disponibles=Coalesce(Subquery(libres, output_field=IntegerField()), 0),
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
