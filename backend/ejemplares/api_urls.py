from django.urls import path

from . import api

# Montado en /api/ejemplares/ (config/urls.py)
urlpatterns = [
    path("", api.lista, name="api_ejemplares"),
    path("<int:pk>/", api.detalle, name="api_ejemplar"),
    path("inventario/", api.inventario, name="api_inventario"),
]
