from __future__ import annotations

from django.test import SimpleTestCase
from src.reviews.domain.value_objects import Rating


class RatingValueObjectTests(SimpleTestCase):
    def test_rating_valid_bounds(self):
        self.assertEqual(Rating(1).value, 1)
        self.assertEqual(Rating(5).value, 5)

    def test_rating_invalid_bounds(self):
        with self.assertRaises(ValueError):
            Rating(0)
        with self.assertRaises(ValueError):
            Rating(6)