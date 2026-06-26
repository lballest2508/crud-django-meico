from rest_framework.routers import DefaultRouter

from apps.catalog.api.viewsets import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
