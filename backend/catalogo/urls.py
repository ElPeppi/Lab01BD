from rest_framework.routers import DefaultRouter

from .views import AutorViewSet, CategoriaViewSet, EditorialViewSet, LibroViewSet

router = DefaultRouter()
router.register("libros", LibroViewSet, basename="libro")
router.register("autores", AutorViewSet)
router.register("editoriales", EditorialViewSet)
router.register("categorias", CategoriaViewSet)

urlpatterns = router.urls