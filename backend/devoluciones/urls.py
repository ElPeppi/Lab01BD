from rest_framework.routers import SimpleRouter

from .views import DevolucionViewSet, MultaViewSet

router = SimpleRouter()
router.register("devoluciones", DevolucionViewSet, basename="devolucion")
router.register("multas", MultaViewSet, basename="multa")

urlpatterns = router.urls