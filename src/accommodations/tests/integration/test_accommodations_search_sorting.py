from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.factories import create_user, create_accommodation
from src.accommodations.infrastructure.orm.models import Accommodation as AccORM


class AccommodationsSearchSortingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # создадим владельца и 3 объявления
        self.host = create_user("sort_host@example.com", roles=["host"])
        self.acc1 = create_accommodation(
            owner_id=self.host.id,
            title="A1",
            description="d",
            city="Berlin",
            region="BE",
            price_cents=10000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )
        self.acc2 = create_accommodation(
            owner_id=self.host.id,
            title="A2",
            description="d",
            city="Berlin",
            region="BE",
            price_cents=20000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )
        self.acc3 = create_accommodation(
            owner_id=self.host.id,
            title="A3",
            description="d",
            city="Berlin",
            region="BE",
            price_cents=30000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )
        # Зададим просмотры/показы напрямую для предсказуемости сортировки
        AccORM.objects.filter(pk=self.acc1.id).update(views_count=5, impressions_count=50)
        AccORM.objects.filter(pk=self.acc2.id).update(views_count=10, impressions_count=30)
        AccORM.objects.filter(pk=self.acc3.id).update(views_count=7, impressions_count=70)

    def test_sort_by_views_desc_stable(self):
        resp = self.client.get("/api/accommodations/search/?only_active=true&page=1&page_size=20&sort=views")
        self.assertEqual(resp.status_code, 200, resp.content)
        items = resp.json()["items"]
        ids = [i["id"] for i in items]
        # Ожидаем порядок по убыванию views_count: acc2(10), acc3(7), acc1(5)
        self.assertTrue(ids.index(self.acc2.id) < ids.index(self.acc3.id) < ids.index(self.acc1.id), ids)
        # Убедимся, что значения действительно в порядке
        vmap = {i["id"]: i["views_count"] for i in items}
        self.assertGreaterEqual(vmap[self.acc2.id], vmap[self.acc3.id])
        self.assertGreaterEqual(vmap[self.acc3.id], vmap[self.acc1.id])

    def test_sort_by_popular_desc_stable(self):
        resp = self.client.get("/api/accommodations/search/?only_active=true&page=1&page_size=20&sort=popular")
        self.assertEqual(resp.status_code, 200, resp.content)
        items = resp.json()["items"]
        ids = [i["id"] for i in items]
        # Ожидаем порядок по убыванию impressions_count: acc3(70), acc1(50), acc2(30)
        self.assertTrue(ids.index(self.acc3.id) < ids.index(self.acc1.id) < ids.index(self.acc2.id), ids)
        imap = {i["id"]: i.get("impressions_count", 0) for i in items}
        self.assertGreaterEqual(imap[self.acc3.id], imap[self.acc1.id])
        self.assertGreaterEqual(imap[self.acc1.id], imap[self.acc2.id])