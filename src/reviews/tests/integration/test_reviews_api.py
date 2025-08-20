# tests/test_reviews_api.py
from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.api import ensure_csrf
from src.shared.testing.factories import create_user, create_accommodation
from src.bookings.infrastructure.orm.models import Booking as BookingORM  # ORM для быстрого статуса
from src.bookings.infrastructure.repositories import DjangoBookingRepository


class ReviewsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.host = create_user("rev_host@example.com", roles=["host"])
        self.guest = create_user("rev_guest@example.com", roles=["guest"])
        self.acc = create_accommodation(
            owner_id=self.host.id,
            title="Reviewed listing",
            description="Desc",
            city="Berlin",
            region="Berlin",
            price_cents=12000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )

    def _create_completed_booking(self) -> int:
        """
        Создаёт бронь через API (guest), подтверждает (host), затем помечает 'completed' напрямую через ORM.
        Возвращает booking_id.
        """
        # guest creates (прошедшие даты, чтобы логически было завершено)
        start = date.today() - timedelta(days=7)
        end = start + timedelta(days=2)
        self.client.force_authenticate(user=self.guest)
        headers = ensure_csrf(self.client)
        payload = {
            "accommodation_id": self.acc.id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }
        resp = self.client.post("/api/bookings/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 201, resp.content)
        booking_id = resp.json()["id"]

        # host confirms
        self.client.force_authenticate(user=self.host)
        headers = ensure_csrf(self.client)
        resp = self.client.post(f"/api/bookings/{booking_id}/confirm/", {}, format="json", **headers)
        self.assertEqual(resp.status_code, 200, resp.content)

        # mark completed via ORM
        obj = BookingORM.objects.get(pk=booking_id)
        obj.status = "completed"
        obj.save(update_fields=["status"])

        # sanity check via repo (optional)
        repo = DjangoBookingRepository()
        dto = repo.get_by_id(booking_id)
        self.assertIsNotNone(dto)
        self.assertEqual(dto.status.value if hasattr(dto.status, "value") else str(dto.status), "completed")

        return booking_id

        # 1) Create review (guest)
        self.client.force_authenticate(user=self.guest)
        headers = ensure_csrf(self.client)
        payload = {
            "booking_id": booking_id,
            "rating": 5,
            "text": "Amazing stay, would return!",
        }
        resp = self.client.post(f"/api/accommodations/{self.acc.id}/reviews/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 201, resp.content)
        review = resp.json()
        review_id = review["id"]

        # Проверим денормализацию на объявлении: 1 отзыв и средний 5.00
        detail = self.client.get(f"/api/accommodations/{self.acc.id}/").json()
        self.assertEqual(detail["reviews_count"], 1)
        # decimal может сериализоваться как строка — приведём к float
        self.assertAlmostEqual(float(detail["average_rating"]), 5.00, places=2)

        # 2) Public list for accommodation
        self.client.force_authenticate(user=None)
        resp = self.client.get(f"/api/accommodations/{self.acc.id}/reviews/")
        self.assertEqual(resp.status_code, 200, resp.content)

        # 3) My reviews (auth required)
        resp = self.client.get("/api/reviews/me/")
        self.assertEqual(resp.status_code, 401, resp.content)
        self.client.force_authenticate(user=self.guest)
        resp = self.client.get("/api/reviews/me/")
        self.assertEqual(resp.status_code, 200, resp.content)

        # 4) Update rating and text (only author)
        headers = ensure_csrf(self.client)
        resp = self.client.patch(
            f"/api/reviews/{review_id}/", {"text": "Updated awesome review!", "rating": 3},
            format="json", **headers
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        # После on_commit средний рейтинг должен обновиться до 3.00
        detail2 = self.client.get(f"/api/accommodations/{self.acc.id}/").json()
        self.assertEqual(detail2["reviews_count"], 1)
        self.assertAlmostEqual(float(detail2["average_rating"]), 3.00, places=2)

        # 5) Negative update by stranger -> 403
        stranger = create_user("rev_stranger@example.com", roles=["guest"])
        self.client.force_authenticate(user=stranger)
        headers = ensure_csrf(self.client)
        resp = self.client.patch(f"/api/reviews/{review_id}/", {"text": "Hack attempt"}, format="json", **headers)
        self.assertEqual(resp.status_code, 403, resp.content)

        # 6) Duplicate create for same booking -> 400
        self.client.force_authenticate(user=self.guest)
        headers = ensure_csrf(self.client)
        payload = {
            "booking_id": booking_id,
            "rating": 4,
            "text": "Another review for the same booking",
        }
        resp = self.client.post(f"/api/accommodations/{self.acc.id}/reviews/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 400, resp.content)

        # 7) Delete (only author) и проверяем, что денормализация обнулилась
        headers = ensure_csrf(self.client)
        resp = self.client.delete(f"/api/reviews/{review_id}/", **headers)
        self.assertEqual(resp.status_code, 204, resp.content)

        detail3 = self.client.get(f"/api/accommodations/{self.acc.id}/").json()
        self.assertEqual(detail3["reviews_count"], 0)
        self.assertAlmostEqual(float(detail3["average_rating"]), 0.00, places=2)


def test_create_review_requires_completed_booking(self):
    # Создадим бронь, но не будем помечать completed
    # guest creates
    start = date.today() - timedelta(days=7)
    end = start + timedelta(days=2)
    self.client.force_authenticate(user=self.guest)
    headers = ensure_csrf(self.client)
    payload = {
        "accommodation_id": self.acc.id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }
    resp = self.client.post("/api/bookings/", payload, format="json", **headers)
    self.assertEqual(resp.status_code, 201, resp.content)
    booking_id = resp.json()["id"]

    # host confirms
    self.client.force_authenticate(user=self.host)
    headers = ensure_csrf(self.client)
    resp = self.client.post(f"/api/bookings/{booking_id}/confirm/", {}, format="json", **headers)
    self.assertEqual(resp.status_code, 200, resp.content)

    # пробуем создать отзыв (не completed) -> 400
    self.client.force_authenticate(user=self.guest)
    headers = ensure_csrf(self.client)
    payload = {
        # accommodation_id убираем из тела, используем path
        "booking_id": booking_id,
        "rating": 5,
        "text": "Should fail because booking is not completed",
    }
    resp = self.client.post(f"/api/accommodations/{self.acc.id}/reviews/", payload, format="json", **headers)
    self.assertEqual(resp.status_code, 400, resp.content)
