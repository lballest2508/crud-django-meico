from decimal import Decimal

from django.test import TestCase

from apps.catalog.api.serializers import CategorySerializer, ProductSerializer
from apps.catalog.models import Category, Product


class CategorySerializerTests(TestCase):
    def test_serializes_all_fields(self) -> None:
        category = Category.objects.create(name="Electronics")
        data = CategorySerializer(instance=category).data
        self.assertEqual(data["name"], "Electronics")
        self.assertIn("id", data)
        self.assertIn("created_at", data)


class ProductSerializerTests(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Laptop",
            price=Decimal("999.99"),
            stock=10,
            category=self.category,
        )

    def test_category_is_nested_on_read(self) -> None:
        data = ProductSerializer(instance=self.product).data
        self.assertIsInstance(data["category"], dict)
        self.assertEqual(data["category"]["name"], "Electronics")
        self.assertEqual(data["category"]["id"], self.category.id)

    def test_category_id_is_write_only(self) -> None:
        data = ProductSerializer(instance=self.product).data
        self.assertNotIn("category_id", data)

    def test_create_via_category_id(self) -> None:
        payload = {
            "name": "Phone",
            "price": "599.99",
            "stock": 5,
            "category_id": self.category.id,
        }
        serializer = ProductSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()
        self.assertEqual(product.category, self.category)

    def test_price_zero_is_invalid(self) -> None:
        payload = {
            "name": "Free Thing",
            "price": "0.00",
            "stock": 1,
            "category_id": self.category.id,
        }
        serializer = ProductSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_price_negative_is_invalid(self) -> None:
        payload = {
            "name": "Negative",
            "price": "-10.00",
            "stock": 1,
            "category_id": self.category.id,
        }
        serializer = ProductSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_price_positive_is_valid(self) -> None:
        payload = {
            "name": "Valid",
            "price": "0.01",
            "stock": 1,
            "category_id": self.category.id,
        }
        serializer = ProductSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_category_id_nullable(self) -> None:
        """category_id can be null because the FK allows null."""
        payload = {
            "name": "Orphan",
            "price": "9.99",
            "stock": 1,
            "category_id": None,
        }
        serializer = ProductSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
