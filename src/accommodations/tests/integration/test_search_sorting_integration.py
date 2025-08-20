from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.factories import create_user, create_accommodation
from src.accommodations.infrastructure.orm.models import Accommodation as AccORM


class SearchSortingIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.host = create_user("sort2_host@example.com", roles=["host"])
        self.a = create_accommodation(
            owner_id=self.host.id,
            title="S1",
            description="d",
            city="Berlin",
            region="BE",
            price_cents=10000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )
        self.b = create_accommodation(
            owner_id=self.host.id,
            title="S2",
            description="d",
            city="Berlin",
            region="BE",
            price_cents=20000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )
        self.c = create_accommodation(
            owner_id=self.host.id,
            title="S3",
            description="d",
            city="Berlin",
            region="BE",
            price_cents=30000,
            rooms=1,
            housing_type="apartment",
            is_active=True,
        )

        AccORM.objects.filter(pk=self.a.id).update(
            views_count=1, impressions_count=100, average_rating=4.50, reviews_count=10
        )
        AccORM.objects.filter(pk=self.b.id).update(
            views_count=50, impressions_count=90, average_rating=4.80, reviews_count=5
        )
        AccORM.objects.filter(pk=self.c.id).update(
            views_count=10, impressions_count=500, average_rating=3.20, reviews_count=20
        )

    def _ids(self, resp):
        self.assertEqual(resp.status_code, 200, resp.content)
        return [i["id"] for i in resp.json()["items"]]

    def test_sort_rating_desc_then_reviews(self):
        # рейтинги: b(4.80), a(4.50), c(3.20)
        r = self.client.get(
            "/api/accommodations/search/?only_active=true&page=1&page_size=20&sort=rating_desc"
        )
        ids = self._ids(r)
        self.assertEqual(ids[:3], [self.b.id, self.a.id, self.c.id])

    def test_sort_reviews_desc(self):
        # отзывы: c(20), a(10), b(5)
        r = self.client.get(
            "/api/accommodations/search/?only_active=true&page=1&page_size=20&sort=reviews_desc"
        )
        ids = self._ids(r)
        self.assertEqual(ids[:3], [self.c.id, self.a.id, self.b.id])

    def test_sort_views_desc(self):
        # просмотры: b(50), c(10), a(1)
        r = self.client.get(
            "/api/accommodations/search/?only_active=true&page=1&page_size=20&sort=views"
        )
        ids = self._ids(r)
        self.assertEqual(ids[:3], [self.b.id, self.c.id, self.a.id])

    def test_sort_popular_desc(self):
        # показы: c(500), a(100), b(90)
        r = self.client.get(
            "/api/accommodations/search/?only_active=true&page=1&page_size=20&sort=popular"
        )
        ids = self._ids(r)
        self.assertEqual(ids[:3], [self.c.id, self.a.id, self.b.id])