from decimal import Decimal

from rest_framework import serializers

from apps.catalog.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""

    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model.

    Returns nested Category on reads; accepts category_id integer on writes.
    """

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = "__all__"

    def validate_price(self, value: Decimal) -> Decimal:
        """Price must be strictly greater than zero."""
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "El precio debe ser mayor que cero."
            )
        return value
