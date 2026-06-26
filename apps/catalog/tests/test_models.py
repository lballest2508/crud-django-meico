from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.catalog.models import Category, Product


class CategoryModelTests(TestCase):
    def test_str_returns_name(self) -> None:
        category = Category.objects.create(name="Electronics")
        self.assertEqual(str(category), "Electronics")

    def test_created_at_is_set_automatically(self) -> None:
        category = Category.objects.create(name="Books")
        self.assertIsNotNone(category.created_at)

    def test_name_must_be_unique(self) -> None:
        Category.objects.create(name="Duplicated")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Duplicated")


class ProductModelTests(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Electronics")

    def test_str_returns_name(self) -> None:
        product = Product.objects.create(
            name="Laptop",
            price=Decimal("999.99"),
            category=self.category,
        )
        self.assertEqual(str(product), "Laptop")

    def test_default_stock_is_zero(self) -> None:
        product = Product.objects.create(
            name="Widget",
            price=Decimal("5.00"),
            category=self.category,
        )
        self.assertEqual(product.stock, 0)

    def test_is_active_default_is_true(self) -> None:
        product = Product.objects.create(
            name="Widget",
            price=Decimal("5.00"),
            category=self.category,
        )
        self.assertTrue(product.is_active)

    def test_created_at_is_set_automatically(self) -> None:
        product = Product.objects.create(
            name="Widget",
            price=Decimal("5.00"),
            category=self.category,
        )
        self.assertIsNotNone(product.created_at)

    def test_negative_price_fails_full_clean(self) -> None:
        """Model validator rejects price < 0 on full_clean()."""
        product = Product(
            name="Bad Price",
            price=Decimal("-1.00"),
            category=self.category,
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_zero_price_passes_model_validator(self) -> None:
        """Model allows price=0; serializer is stricter (> 0)."""
        product = Product(
            name="Free",
            price=Decimal("0.00"),
            category=self.category,
        )
        try:
            product.full_clean()
        except ValidationError:
            self.fail(
                "Model should allow price=0;"
                " stricter validation is in the serializer."
            )

    def test_category_set_null_on_category_delete(self) -> None:
        """Deleting a category sets product.category to NULL (SET_NULL)."""
        product = Product.objects.create(
            name="Laptop",
            price=Decimal("999.99"),
            category=self.category,
        )
        self.category.delete()
        product.refresh_from_db()
        self.assertIsNone(product.category)
