from apps.catalog.models import Category, Product
from rest_framework import serializers
from django.core.validators import MinValueValidator


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        """
        Meta class for the CategorySerializer.
        """
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        """
        Meta class for the ProductSerializer.
        """
        model = Product
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Product instance.
    """
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        """
        Meta class for the ProductCreateSerializer.
        """
        model = Product
        fields = ['name', 'description', 'price',
                  'stock', 'category', 'is_active']
