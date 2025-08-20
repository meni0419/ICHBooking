from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.factories import create_user, create_accommodation


class SearchApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = create_user("owner@example.com")
        self.acc = create_accommodation(
            owner_id=self.owner.id,
            title="Nice apartment near center",
            description="Great location",
            city="München",
            region="Bayern",
            price_cents=99000,
            rooms=2,
            housing_type="apartment",
            is_active=True,
        )

    def test_impressions_increment_on_filtered_search(self):
        # Базовое значение
        self.acc.refresh_from_db()
        base = self.acc.impressions_count

        # Фильтр по city — должен инкрементировать всем найденным
        resp = self.client.get("/api/accommodations/search/", {"city": "München"})
        self.assertEqual(resp.status_code, 200, resp.content)

        self.acc.refresh_from_db()
        self.assertEqual(self.acc.impressions_count, base + 1)

        # Повторяем ещё раз — счётчик должен снова вырасти
        resp = self.client.get("/api/accommodations/search/", {"city": "München"})
        self.assertEqual(resp.status_code, 200, resp.content)

        self.acc.refresh_from_db()
        self.assertEqual(self.acc.impressions_count, base + 2)

    def test_unfiltered_search_does_not_increment(self):
        self.acc.refresh_from_db()
        base = self.acc.impressions_count

        # Без фильтров (только пагинация/сортировка по умолчанию) — не считаем показ
        resp = self.client.get("/api/accommodations/search/")
        self.assertEqual(resp.status_code, 200, resp.content)

        self.acc.refresh_from_db()
        self.assertEqual(self.acc.impressions_count, base)
