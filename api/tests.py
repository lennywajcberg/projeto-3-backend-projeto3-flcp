from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Favorite
from . import views


class SymbolsViewTests(APITestCase):
    def test_symbols_returns_allowed_catalog(self):
        response = self.client.get("/api/symbols")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload["symbols"], views.ALLOWED_SYMBOLS)

    def test_symbols_is_idempotent(self):
        first = self.client.get("/api/symbols").json()
        second = self.client.get("/api/symbols").json()
        self.assertEqual(first, second)


class QuotesViewTests(APITestCase):
    def setUp(self):
        self.cid = "test-client"

    def _mock_upstream(self, payload):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = payload
        return mock_response

    @patch("api.views.requests.get")
    def test_quotes_returns_data_and_marks_favorites(self, mock_get):
        Favorite.objects.create(client_id=self.cid, symbol="USD-BRL")
        mock_get.return_value = self._mock_upstream(
            {
                "USDBRL": {
                    "bid": "5.10",
                    "pctChange": "1.2",
                    "create_date": "2025-10-13 10:00:00",
                }
            }
        )

        response = self.client.get(
            "/api/quotes?symbols=USD-BRL",
            HTTP_X_CLIENT_ID=self.cid,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        quotes = response.json()["quotes"]
        self.assertEqual(len(quotes), 1)
        quote = quotes[0]
        self.assertEqual(quote["symbol"], "USD-BRL")
        self.assertTrue(quote["isFavorite"])
        self.assertAlmostEqual(quote["price"], 5.10, places=2)
        self.assertEqual(quote["changePct"], 1.2)

    @patch("api.views.requests.get", side_effect=Exception("boom"))
    def test_quotes_handles_upstream_error(self, _mock_get):
        response = self.client.get("/api/quotes")
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        payload = response.json()
        self.assertEqual(payload["error"], "failed_upstream")


class FavoritesCollectionTests(APITestCase):
    def setUp(self):
        self.cid = "fav-client"

    def test_get_favorites_requires_header(self):
        response = self.client.get("/api/favorites")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_favorites_returns_symbols(self):
        Favorite.objects.create(client_id=self.cid, symbol="USD-BRL")
        Favorite.objects.create(client_id=self.cid, symbol="EUR-BRL")

        response = self.client.get("/api/favorites", HTTP_X_CLIENT_ID=self.cid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertCountEqual(payload["favorites"], ["USD-BRL", "EUR-BRL"])

    def test_post_creates_favorite(self):
        response = self.client.post(
            "/api/favorites",
            {"symbol": "USD-BRL"},
            format="json",
            HTTP_X_CLIENT_ID=self.cid,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(client_id=self.cid, symbol="USD-BRL").exists())

    def test_post_rejects_invalid_symbol(self):
        response = self.client.post(
            "/api/favorites",
            {"symbol": "INVALID"},
            format="json",
            HTTP_X_CLIENT_ID=self.cid,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid_symbol", response.json()["error"])


class FavoritesDetailTests(APITestCase):
    def setUp(self):
        self.cid = "detail-client"

    def test_delete_requires_header(self):
        response = self.client.delete("/api/favorites/USD-BRL")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_removes_favorite(self):
        Favorite.objects.create(client_id=self.cid, symbol="USD-BRL")

        response = self.client.delete("/api/favorites/USD-BRL", HTTP_X_CLIENT_ID=self.cid)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(client_id=self.cid, symbol="USD-BRL").exists())

    def test_delete_unknown_favorite_returns_not_found(self):
        response = self.client.delete("/api/favorites/USD-BRL", HTTP_X_CLIENT_ID=self.cid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
