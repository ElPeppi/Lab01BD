from rest_framework.routers import SimpleRouter

from .views import UsuarioViewSet

router = SimpleRouter()
router.register("", UsuarioViewSet, basename="usuario")

urlpatterns = router.urls
