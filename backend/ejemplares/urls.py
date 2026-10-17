from django.urls import path

from . import views

app_name = "ejemplares"

urlpatterns = [
    # Vistas HTML de Ejemplares Físicos (CRUD)
    path("", views.lista_ejemplares, name="lista"),
    path("nuevo/", views.crear_ejemplar, name="crear"),
    path("<int:pk>/", views.detalle_ejemplar, name="detalle"),
    path("<int:pk>/editar/", views.editar_ejemplar, name="editar"),
    path("<int:pk>/baja/", views.dar_baja_ejemplar, name="dar_baja"),
    path("<int:pk>/reactivar/", views.reactivar_ejemplar, name="reactivar"),
    # Reporte de Inventario por Estado
    path("inventario/", views.reporte_inventario, name="reporte_inventario"),
    # Endpoints JSON / API
    path("api/", views.api_ejemplares, name="api_lista"),
    path("api/<int:pk>/", views.api_detalle_ejemplar, name="api_detalle"),
    path("api/inventario/", views.api_reporte_inventario, name="api_inventario"),
]
