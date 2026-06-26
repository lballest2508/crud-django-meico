from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Category, Product


class ProductViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Laptop",
            price=Decimal("999.99"),
            stock=10,
            category=self.category,
        )
        self.list_url = "/api/products/"
        self.detail_url = f"/api/products/{self.product.id}/"
        self.adjust_url = f"/api/products/{self.product.id}/adjust_stock/"

    # --- CRUD ---

    def test_list_returns_200(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_list_only_shows_active_products(self) -> None:
        inactive = Product.objects.create(
            name="Inactive",
            price=Decimal("1.00"),
            category=self.category,
            is_active=False,
        )
        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]
        self.assertIn("Laptop", names)
        self.assertNotIn(inactive.name, names)

    def test_create_returns_201(self) -> None:
        payload = {
            "name": "Phone",
            "price": "599.99",
            "stock": 5,
            "category_id": self.category.id,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Phone")

    def test_retrieve_returns_200(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop")

    def test_retrieve_returns_nested_category(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertIsInstance(response.data["category"], dict)
        self.assertEqual(response.data["category"]["name"], "Electronics")

    def test_update_returns_200(self) -> None:
        payload = {
            "name": "Updated Laptop",
            "price": "1099.99",
            "stock": 8,
            "category_id": self.category.id,
        }
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Laptop")

    def test_partial_update_returns_200(self) -> None:
        response = self.client.patch(
            self.detail_url, {"name": "Laptop Pro"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop Pro")

    def test_destroy_returns_204(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_sets_is_active_false(self) -> None:
        self.client.delete(self.detail_url)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_soft_deleted_product_absent_from_list(self) -> None:
        self.client.delete(self.detail_url)
        response = self.client.get(self.list_url)
        names = [p["name"] for p in response.data["results"]]
        self.assertNotIn("Laptop", names)

    def test_soft_deleted_product_not_retrievable(self) -> None:
        self.client.delete(self.detail_url)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Filtros ---

    def test_filter_by_category_id(self) -> None:
        other_cat = Category.objects.create(name="Books")
        Product.objects.create(
            name="Novel",
            price=Decimal("9.99"),
            category=other_cat,
        )
        response = self.client.get(
            self.list_url, {"category_id": self.category.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for product in response.data["results"]:
            self.assertEqual(product["category"]["id"], self.category.id)

    def test_search_by_name(self) -> None:
        response = self.client.get(self.list_url, {"search": "Lap"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)
        self.assertTrue(
            all("Lap" in p["name"] for p in response.data["results"])
        )

    def test_search_no_match_returns_empty(self) -> None:
        response = self.client.get(
            self.list_url, {"search": "NONEXISTENT_XYZ"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    # --- Validación al crear ---

    def test_create_with_zero_price_returns_400(self) -> None:
        payload = {
            "name": "Free",
            "price": "0.00",
            "stock": 1,
            "category_id": self.category.id,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_create_with_negative_price_returns_400(self) -> None:
        payload = {
            "name": "Negative",
            "price": "-5.00",
            "stock": 1,
            "category_id": self.category.id,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- adjust_stock ---

    def test_adjust_stock_positive(self) -> None:
        response = self.client.post(
            self.adjust_url, {"quantity": 5}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_anterior"], 10)
        self.assertEqual(response.data["ajuste"], 5)
        self.assertEqual(response.data["stock_actual"], 15)

    def test_adjust_stock_negative(self) -> None:
        response = self.client.post(
            self.adjust_url, {"quantity": -3}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_actual"], 7)

    def test_adjust_stock_to_zero_is_allowed(self) -> None:
        response = self.client.post(
            self.adjust_url, {"quantity": -10}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_actual"], 0)

    def test_adjust_stock_below_zero_returns_400(self) -> None:
        response = self.client.post(
            self.adjust_url, {"quantity": -100}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_adjust_stock_on_zero_stock_negative_returns_400(self) -> None:
        self.product.stock = 0
        self.product.save()
        response = self.client.post(
            self.adjust_url, {"quantity": -1}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adjust_stock_missing_quantity_returns_400(self) -> None:
        response = self.client.post(self.adjust_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_adjust_stock_string_quantity_returns_400(self) -> None:
        response = self.client.post(
            self.adjust_url, {"quantity": "abc"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_adjust_stock_float_quantity_returns_400(self) -> None:
        response = self.client.post(
            self.adjust_url, {"quantity": 1.5}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_adjust_stock_persists_to_db(self) -> None:
        self.client.post(self.adjust_url, {"quantity": 5}, format="json")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 15)


class CategoryViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Electronics")
        self.list_url = "/api/categories/"
        self.detail_url = f"/api/categories/{self.category.id}/"

    def test_list_returns_200(self) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_returns_201(self) -> None:
        response = self.client.post(
            self.list_url, {"name": "Books"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Books")

    def test_retrieve_returns_200(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Electronics")

    def test_update_returns_200(self) -> None:
        response = self.client.put(
            self.detail_url, {"name": "Tech"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Tech")

    def test_partial_update_returns_200(self) -> None:
        response = self.client.patch(
            self.detail_url, {"name": "Gadgets"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Gadgets")

    def test_delete_removes_category(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
