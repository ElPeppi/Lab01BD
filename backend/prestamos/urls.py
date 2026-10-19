from rest_framework.routers import SimpleRouter

from .views import PrestamoViewSet

router = SimpleRouter()
router.register("", PrestamoViewSet, basename="prestamo")

urlpatterns = router.urls
