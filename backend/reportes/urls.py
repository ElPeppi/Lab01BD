from django.urls import path
from .views import (
    ResumenReportesView,
    LibrosPopularesView,
    MorososView,
    PrestamosPeriodoView,
    MultasRecaudoView,
    UsuariosActividadView,
    ExportarCSVReportesView,
)

app_name = "reportes"

urlpatterns = [
    path("resumen/", ResumenReportesView.as_view(), name="resumen"),
    path("libros-populares/", LibrosPopularesView.as_view(), name="libros_populares"),
    path("morosos/", MorososView.as_view(), name="morosos"),
    path("prestamos-periodo/", PrestamosPeriodoView.as_view(), name="prestamos_periodo"),
    path("multas-recaudo/", MultasRecaudoView.as_view(), name="multas_recaudo"),
    path("usuarios-actividad/", UsuariosActividadView.as_view(), name="usuarios_actividad"),
    path("exportar/", ExportarCSVReportesView.as_view(), name="exportar_csv"),
]
