from __future__ import annotations

from django.test import SimpleTestCase

from src.common.infrastructure.repositories import build_query_signature


class BuildQuerySignatureTests(SimpleTestCase):
    def test_signature_normalizes_and_sorts(self):
        built = build_query_signature(
            keyword=" квартира ",
            city="  München ",
            region="  Bayern ",
            price_min=100.0,
            price_max=1000.0,
            rooms_min=1,
            rooms_max=3,
            housing_types=["studio", "apartment", "apartment", "  room  "],
        )
        norm = built["norm"]
        sig = built["signature"]

        # housing_types: uniq + sort
        self.assertEqual(norm["housing_types"], ["apartment", "room", "studio"])
        # strings trimmed
        self.assertEqual(norm["keyword"], "квартира")
        self.assertEqual(norm["city"], "München")
        self.assertEqual(norm["region"], "Bayern")
        # signature should contain stabilized list order
        self.assertIn("housing_types=apartment,room,studio", sig)
        self.assertIn("keyword=квартира", sig)
        self.assertIn("city=München", sig)
        self.assertIn("region=Bayern", sig)

    def test_signature_empty_when_no_filters(self):
        built = build_query_signature(
            keyword=None,
            city=None,
            region=None,
            price_min=None,
            price_max=None,
            rooms_min=None,
            rooms_max=None,
            housing_types=[],
        )
        self.assertEqual(built["signature"], "")