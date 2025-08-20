from __future__ import annotations

from django.test import SimpleTestCase

from src.accommodations.domain.entities import Accommodation
from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType


def make_entity() -> Accommodation:
    return Accommodation(
        id=None,
        owner_id=42,
        title="Initial title",
        description="Initial long enough description",
        location=Location(city="Munich", region="Bayern", country="DE"),
        price=Price(amount_cents=12345),
        rooms=RoomsCount(2),
        housing_type=HousingType("apartment"),
        is_active=True,
    )


class AccommodationEntityTests(SimpleTestCase):
    def test_rename_success(self):
        acc = make_entity()
        acc.rename("New title")
        self.assertEqual(acc.title, "New title")

    def test_rename_invalid(self):
        acc = make_entity()
        with self.assertRaises(ValueError):
            acc.rename("  ")

    def test_change_description_success(self):
        acc = make_entity()
        acc.change_description("New valid description text")
        self.assertEqual(acc.description, "New valid description text")

    def test_change_description_invalid(self):
        acc = make_entity()
        with self.assertRaises(ValueError):
            acc.change_description("short")

    def test_toggle_active_switch(self):
        acc = make_entity()
        self.assertTrue(acc.is_active)
        acc.toggle_active()
        self.assertFalse(acc.is_active)
        acc.toggle_active()
        self.assertTrue(acc.is_active)

    def test_toggle_active_explicit_true_false(self):
        acc = make_entity()
        acc.toggle_active(False)
        self.assertFalse(acc.is_active)
        acc.toggle_active(True)
        self.assertTrue(acc.is_active)

    def test_setters_price_rooms_type(self):
        acc = make_entity()
        acc.set_price(Price(amount_cents=9999))
        acc.set_rooms(RoomsCount(3))
        acc.set_housing_type(HousingType("studio"))
        self.assertEqual(acc.price.amount_cents, 9999)
        self.assertEqual(acc.rooms.value, 3)
        self.assertEqual(acc.housing_type.value if hasattr(acc.housing_type, "value") else acc.housing_type, "studio")

    def test_default_counters_are_zero(self):
        acc = make_entity()
        self.assertEqual(acc.impressions_count, 0)
        self.assertEqual(acc.views_count, 0)
        self.assertEqual(acc.reviews_count, 0)
        self.assertAlmostEqual(acc.average_rating, 0.0, places=2)
