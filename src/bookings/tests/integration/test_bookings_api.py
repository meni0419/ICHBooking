from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.api import ensure_csrf
from src.shared.testing.factories import create_user, create_accommodation


class BookingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Хост-владелец объявления
        self.host = create_user("host@example.com", roles=["host"])
        # Гость
        self.guest = create_user("guest@example.com", roles=["guest"])
        # Объявление хоста
        self.acc = create_accommodation(
            owner_id=self.host.id,
            title="Listing for booking",
            description="Nice place",
            city="Berlin",
            region="Berlin",
            price_cents=20000,
            rooms=2,
            housing_type="apartment",
            is_active=True,
        )

    def _create_booking_via_api(self, start: date, end: date) -> dict:
        """Создание бронирования через API от имени гостя. Возвращает JSON брони."""
        self.client.force_authenticate(user=self.guest)
        headers = ensure_csrf(self.client)
        payload = {
            "accommodation_id": self.acc.id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
        resp = self.client.post("/api/bookings/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 201, resp.content)
        return resp.json()

    def test_guest_can_create_booking(self):
        start = date.today() + timedelta(days=10)
        end = start + timedelta(days=3)
        booking = self._create_booking_via_api(start, end)
        self.assertEqual(booking["guest_id"], self.guest.id)
        self.assertEqual(booking["host_id"], self.host.id)
        self.assertEqual(booking["accommodation_id"], self.acc.id)
        self.assertEqual(booking["status"], "requested")

    def test_booking_detail_access(self):
        start = date.today() + timedelta(days=7)
        end = start + timedelta(days=2)
        booking = self._create_booking_via_api(start, end)
        booking_id = booking["id"]

        # Доступ у гостя
        self.client.force_authenticate(user=self.guest)
        resp = self.client.get(f"/api/bookings/{booking_id}/")
        self.assertEqual(resp.status_code, 200, resp.content)

        # Доступ у хоста
        self.client.force_authenticate(user=self.host)
        resp = self.client.get(f"/api/bookings/{booking_id}/")
        self.assertEqual(resp.status_code, 200, resp.content)

        # Посторонний пользователь — 403
        stranger = create_user("stranger@example.com", roles=["guest"])
        self.client.force_authenticate(user=stranger)
        resp = self.client.get(f"/api/bookings/{booking_id}/")
        self.assertEqual(resp.status_code, 403, resp.content)

    def test_host_can_confirm_and_reject(self):
        start = date.today() + timedelta(days=8)
        end = start + timedelta(days=2)
        booking = self._create_booking_via_api(start, end)
        booking_id = booking["id"]

        # Подтвердить (host)
        self.client.force_authenticate(user=self.host)
        headers = ensure_csrf(self.client)
        resp = self.client.post(f"/api/bookings/{booking_id}/confirm/", {}, format="json", **headers)
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "confirmed")

        # Создаём ещё одну бронь -> отклоняем
        booking2 = self._create_booking_via_api(start + timedelta(days=5), end + timedelta(days=5))
        booking2_id = booking2["id"]

        self.client.force_authenticate(user=self.host)
        headers = ensure_csrf(self.client)
        resp = self.client.post(f"/api/bookings/{booking2_id}/reject/", {}, format="json", **headers)
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "rejected")

    def test_guest_cancel_before_deadline(self):
        # Создаём REQUESTED с началом через 10 дней — гость может отменить до дедлайна
        start = date.today() + timedelta(days=10)
        end = start + timedelta(days=3)
        booking = self._create_booking_via_api(start, end)
        booking_id = booking["id"]

        self.client.force_authenticate(user=self.guest)
        headers = ensure_csrf(self.client)
        resp = self.client.post(f"/api/bookings/{booking_id}/cancel/", {}, format="json", **headers)
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "cancelled")

    def test_host_cancel_before_start(self):
        # Создаём, затем подтверждаем, затем хост отменяет до старта
        start = date.today() + timedelta(days=5)
        end = start + timedelta(days=2)
        booking = self._create_booking_via_api(start, end)
        booking_id = booking["id"]

        # confirm
        self.client.force_authenticate(user=self.host)
        headers = ensure_csrf(self.client)
        resp = self.client.post(f"/api/bookings/{booking_id}/confirm/", {}, format="json", **headers)
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "confirmed")

        # cancel by host
        headers = ensure_csrf(self.client)
        resp = self.client.post(f"/api/bookings/{booking_id}/cancel/", {}, format="json", **headers)
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()["status"], "cancelled")

    def test_lists_me_and_requests_for_host(self):
        # Создаём две брони от имени guest (REQUESTED)
        start = date.today() + timedelta(days=9)
        end = start + timedelta(days=2)
        b1 = self._create_booking_via_api(start, end)
        b2 = self._create_booking_via_api(start + timedelta(days=4), end + timedelta(days=4))

        # /bookings/me/ под гостем — обе должны быть в списке
        self.client.force_authenticate(user=self.guest)
        resp = self.client.get("/api/bookings/me/")
        self.assertEqual(resp.status_code, 200, resp.content)
        ids = [item["id"] for item in resp.json()]
        self.assertIn(b1["id"], ids)
        self.assertIn(b2["id"], ids)

        # /bookings/requests/ под хостом — обе REQUESTED попадают
        self.client.force_authenticate(user=self.host)
        resp = self.client.get("/api/bookings/requests/")
        self.assertEqual(resp.status_code, 200, resp.content)
        ids = [item["id"] for item in resp.json()]
        self.assertIn(b1["id"], ids)
        self.assertIn(b2["id"], ids)
