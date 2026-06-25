from django.urls import path
from .api.viewsets import ProductViewSet, ProductCreateViewSet, CategoryViewSet


urlpatterns = [
    path('products/',
         ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('products/create/',
         ProductCreateViewSet.as_view({'post': 'create'}), name='product-create'),
    path('categories/',
         CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
]
