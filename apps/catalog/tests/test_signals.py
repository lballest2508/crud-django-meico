from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from apps.catalog.models import Category, Product


class ProductPostSaveSignalTests(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Electronics")

    def test_signal_fires_on_create(self) -> None:
        with patch("builtins.print") as mock_print:
            Product.objects.create(
                name="Laptop",
                price=Decimal("999.99"),
                stock=10,
                category=self.category,
            )
            mock_print.assert_called()

    def test_signal_message_format_on_create(self) -> None:
        with patch("builtins.print") as mock_print:
            Product.objects.create(
                name="Laptop",
                price=Decimal("999.99"),
                stock=10,
                category=self.category,
            )
            mock_print.assert_called_with(
                '[CATALOG] Producto "Laptop" actualizado. Stock actual: 10'
            )

    def test_signal_fires_on_update(self) -> None:
        product = Product.objects.create(
            name="Laptop",
            price=Decimal("999.99"),
            stock=10,
            category=self.category,
        )
        with patch("builtins.print") as mock_print:
            product.stock = 25
            product.save()
            mock_print.assert_called_with(
                '[CATALOG] Producto "Laptop" actualizado. Stock actual: 25'
            )

    def test_signal_message_includes_product_name_and_stock(self) -> None:
        with patch("builtins.print") as mock_print:
            Product.objects.create(
                name="Special Gadget",
                price=Decimal("49.99"),
                stock=3,
                category=self.category,
            )
            args, _ = mock_print.call_args
            self.assertIn("[CATALOG]", args[0])
            self.assertIn("Special Gadget", args[0])
            self.assertIn("3", args[0])
