from apps.catalog.models import Category, Product
from rest_framework import viewsets, status
from apps.catalog.api.serializers import ProductSerializer, ProductCreateSerializer, CategorySerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction


class ProductViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing product instances.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        cdelaossa@meico.com.co
        Returns a queryset of active products,
        optionally filtered by category and search term.
        """
        queryset = Product.objects.filter(is_active=True)

        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='adjust_stock')
    def adjust_stock(self, request, pk=None):
        """
        Adjust the stock of a product.
        """
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'error': 'El campo quantity es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(quantity, int):
            return Response(
                {'error': 'El campo quantity debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=pk)

            new_stock = product.stock + quantity
            if new_stock < 0:
                return Response(
                    {
                        'error': f'Stock insuficiente. Stock actual: {product.stock}, '
                                 f'ajuste solicitado: {quantity}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            product.stock = new_stock
            product.save(update_fields=['stock'])

        return Response(
            {
                'id': product.id,
                'stock_anterior': product.stock - quantity,
                'ajuste': quantity,
                'stock_actual': product.stock,
            },
            status=status.HTTP_200_OK
        )


class ProductCreateViewSet(viewsets.ModelViewSet):
    """
    A viewset for creating product instances.
    """
    serializer_class = ProductCreateSerializer
    queryset = Product.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing category instances.
    """
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
