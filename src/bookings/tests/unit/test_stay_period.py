from __future__ import annotations

from datetime import date

from django.test import SimpleTestCase

from src.bookings.domain.value_objects import StayPeriod


class StayPeriodTests(SimpleTestCase):
    def test_init_valid_and_days(self):
        p = StayPeriod(date(2025, 1, 1), date(2025, 1, 10))
        self.assertEqual(p.days(), 9)

    def test_init_invalid_end_le_start(self):
        with self.assertRaises(ValueError):
            StayPeriod(date(2025, 1, 10), date(2025, 1, 10))
        with self.assertRaises(ValueError):
            StayPeriod(date(2025, 1, 10), date(2025, 1, 5))

    def test_overlaps(self):
        a = StayPeriod(date(2025, 1, 1), date(2025, 1, 10))
        # полное пересечение
        self.assertTrue(a.overlaps(StayPeriod(date(2025, 1, 5), date(2025, 1, 15))))
        # соприкасаются концами (полуинтервалы) — не пересекаются
        self.assertFalse(a.overlaps(StayPeriod(date(2025, 1, 10), date(2025, 1, 12))))
        self.assertFalse(a.overlaps(StayPeriod(date(2024, 12, 20), date(2025, 1, 1))))