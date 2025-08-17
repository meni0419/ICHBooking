from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.factories import create_user, create_accommodation
from src.shared.testing.api import ensure_csrf


class AccommodationsApiPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Пользователь-владелец с ролью host
        self.host_owner = create_user("owner@example.com", roles=["host"])
        # Другой пользователь-гость (без host)
        self.guest_user = create_user("guest@example.com", roles=["guest"])
        # Создаём объявление напрямую через ORM (владельцем — host)
        self.acc = create_accommodation(
            owner_id=self.host_owner.id,
            title="My listing",
            description="Long enough description",
            city="Berlin",
            region="Berlin",
            price_cents=12000,
            rooms=2,
            housing_type="apartment",
            is_active=True,
        )

    # ---------- Публичный доступ ----------
    def test_get_detail_public_ok(self):
        resp = self.client.get(f"/api/accommodations/{self.acc.id}/")
        self.assertEqual(resp.status_code, 200, resp.content)
        data = resp.json()
        self.assertEqual(data["id"], self.acc.id)
        self.assertEqual(data["title"], "My listing")

    # ---------- Создание ----------
    def test_create_forbidden_for_guest(self):
        # Неаутентифицированный — 401 (нет аутентификации)
        headers = ensure_csrf(self.client)
        payload = {
            "title": "New acc",
            "description": "Some description long enough",
            "city": "München",
            "region": "Bayern",
            "price_eur": 100.0,
            "rooms": 1,
            "housing_type": "apartment",
            "is_active": True,
        }
        resp = self.client.post("/api/accommodations/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 401, resp.content)

        # Аутентифицированный, но guest — 403 (нет роли host)
        self.client.force_authenticate(user=self.guest_user)
        headers = ensure_csrf(self.client)
        resp = self.client.post("/api/accommodations/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 403, resp.content)

    def test_create_success_for_host(self):
        self.client.force_authenticate(user=self.host_owner)
        headers = ensure_csrf(self.client)
        payload = {
            "title": "Brand new listing",
            "description": "Nice brand new description",
            "city": "Hamburg",
            "region": "Hamburg",
            "price_eur": 150.0,
            "rooms": 2,
            "housing_type": "apartment",
            "is_active": True,
        }
        resp = self.client.post("/api/accommodations/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data["owner_id"], self.host_owner.id)
        self.assertEqual(data["city"], "Hamburg")

    # ---------- Обновление ----------
    def test_patch_forbidden_for_guest(self):
        self.client.force_authenticate(user=self.guest_user)
        headers = ensure_csrf(self.client)
        resp = self.client.patch(
            f"/api/accommodations/{self.acc.id}/",
            {"title": "Updated"},
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 403, resp.content)

    def test_patch_success_for_owner_host(self):
        self.client.force_authenticate(user=self.host_owner)
        headers = ensure_csrf(self.client)
        resp = self.client.patch(
            f"/api/accommodations/{self.acc.id}/",
            {"title": "Updated by owner"},
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["title"], "Updated by owner")

    # ---------- Toggle ----------
    def test_toggle_forbidden_for_guest(self):
        self.client.force_authenticate(user=self.guest_user)
        headers = ensure_csrf(self.client)
        resp = self.client.post(
            f"/api/accommodations/{self.acc.id}/toggle/",
            {"is_active": False},
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 403, resp.content)

    def test_toggle_success_for_owner_host(self):
        self.client.force_authenticate(user=self.host_owner)
        headers = ensure_csrf(self.client)
        resp = self.client.post(
            f"/api/accommodations/{self.acc.id}/toggle/",
            {"is_active": False},
            format="json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertFalse(resp.json()["is_active"])

    # ---------- Удаление ----------
    def test_delete_forbidden_for_guest(self):
        self.client.force_authenticate(user=self.guest_user)
        headers = ensure_csrf(self.client)
        resp = self.client.delete(f"/api/accommodations/{self.acc.id}/", **headers)
        self.assertEqual(resp.status_code, 403, resp.content)

    def test_delete_success_for_owner_host(self):
        self.client.force_authenticate(user=self.host_owner)
        headers = ensure_csrf(self.client)
        resp = self.client.delete(f"/api/accommodations/{self.acc.id}/", **headers)
        self.assertEqual(resp.status_code, 204, resp.content)

    # ---------- “Мои объявления” ----------
    def test_list_mine_forbidden_for_guest(self):
        # Неаутентифицированный — 401
        resp = self.client.get("/api/accommodations/mine/")
        self.assertEqual(resp.status_code, 401, resp.content)

        # Аутентифицированный guest — 403 (нет роли host)
        self.client.force_authenticate(user=self.guest_user)
        resp = self.client.get("/api/accommodations/mine/")
        self.assertEqual(resp.status_code, 403, resp.content)

    def test_list_mine_success_for_host(self):
        self.client.force_authenticate(user=self.host_owner)
        resp = self.client.get("/api/accommodations/mine/")
        self.assertEqual(resp.status_code, 200, resp.content)
        items = resp.json()
        self.assertTrue(any(item["id"] == self.acc.id for item in items), items)
