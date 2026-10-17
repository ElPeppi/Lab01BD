from django.contrib import admin

from .models import Ejemplar


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = (
        "id_ejemplar",
        "codigo_barras",
        "libro",
        "ubicacion",
        "estado",
        "condicion",
        "eliminado",
    )
    list_filter = ("estado", "condicion", "eliminado")
    search_fields = ("codigo_barras", "ubicacion", "libro__titulo", "libro__isbn")
    list_select_related = ("libro",)
    actions = ["dar_de_baja_seleccionados", "reactivar_seleccionados"]

    @admin.action(description="Dar de baja ejemplares seleccionados (solo no prestados)")
    def dar_de_baja_seleccionados(self, request, queryset):
        actualizados = queryset.exclude(estado=Ejemplar.ESTADO_PRESTADO).update(eliminado=True)
        self.message_user(request, f"{actualizados} ejemplar(es) dados de baja correctamente.")

    @admin.action(description="Reactivar ejemplares seleccionados")
    def reactivar_seleccionados(self, request, queryset):
        actualizados = queryset.update(eliminado=False)
        self.message_user(request, f"{actualizados} ejemplar(es) reactivados correctamente.")

