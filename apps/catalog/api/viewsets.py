from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.catalog.api.serializers import CategorySerializer, ProductSerializer
from apps.catalog.models import Category, Product


@extend_schema_view(
    list=extend_schema(
        summary="Listar productos activos",
        parameters=[
            OpenApiParameter(
                "category_id",
                OpenApiTypes.INT,
                description="Filtrar por ID de categoría",
            ),
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                description="Búsqueda parcial por nombre de producto",
            ),
        ],
    ),
    create=extend_schema(summary="Crear un producto"),
    retrieve=extend_schema(summary="Obtener detalle de un producto"),
    update=extend_schema(summary="Actualizar un producto completo"),
    partial_update=extend_schema(summary="Actualizar campos de un producto"),
    destroy=extend_schema(summary="Desactivar un producto (soft delete)"),
)
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para ver, crear, actualizar y desactivar productos."""

    serializer_class = ProductSerializer

    def get_queryset(self) -> QuerySet[Product]:
        """Retorna productos activos.

        Filtros opcionales por categoría y nombre.
        """
        queryset: QuerySet[Product] = Product.objects.filter(is_active=True)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Soft delete: marca is_active=False en lugar de borrar."""
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Ajustar stock de un producto",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "quantity": {
                        "type": "integer",
                        "description": (
                            "Cantidad a sumar (positivo)"
                            " o restar (negativo)"
                        ),
                    }
                },
                "required": ["quantity"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "stock_anterior": {"type": "integer"},
                    "ajuste": {"type": "integer"},
                    "stock_actual": {"type": "integer"},
                },
            },
            400: {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    )
    @action(detail=True, methods=["post"], url_path="adjust_stock")
    def adjust_stock(
        self, request: Request, pk: str | None = None
    ) -> Response:
        """Ajusta stock de forma atómica. Impide stock negativo."""
        quantity = request.data.get("quantity")
        if quantity is None:
            return Response(
                {"error": "El campo quantity es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(quantity, int):
            return Response(
                {"error": "El campo quantity debe ser un número entero."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=pk)
            new_stock = product.stock + quantity
            if new_stock < 0:
                return Response(
                    {
                        "error": (
                            "Stock insuficiente. "
                            f"Stock actual: {product.stock}, "
                            f"ajuste solicitado: {quantity}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            previous_stock = product.stock
            product.stock = new_stock
            product.save(update_fields=["stock"])

        return Response(
            {
                "id": product.id,
                "stock_anterior": previous_stock,
                "ajuste": quantity,
                "stock_actual": product.stock,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(summary="Listar categorías"),
    create=extend_schema(summary="Crear una categoría"),
    retrieve=extend_schema(summary="Obtener detalle de una categoría"),
    update=extend_schema(summary="Actualizar una categoría completa"),
    partial_update=extend_schema(summary="Actualizar campos de una categoría"),
    destroy=extend_schema(summary="Eliminar una categoría"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para ver y editar categorías."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
