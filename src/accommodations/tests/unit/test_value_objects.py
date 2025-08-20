from __future__ import annotations

from django.test import SimpleTestCase

from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType


class ValueObjectsTests(SimpleTestCase):
    def test_location_basic(self):
        loc = Location(city="Berlin", region="Berlin", country="DE")
        self.assertEqual(loc.city, "Berlin")
        self.assertEqual(loc.region, "Berlin")
        self.assertEqual(loc.country, "DE")

    def test_price_and_rooms(self):
        p = Price(amount_cents=12345)
        self.assertEqual(p.amount_cents, 12345)
        self.assertAlmostEqual(p.as_euros(), 123.45, places=2)

        r = RoomsCount(3)
        self.assertEqual(r.value, 3)

    def test_housing_type_enum(self):
        self.assertEqual(HousingType("apartment").value, "apartment")
        # совместимость со строковым представлением
        self.assertEqual(str(HousingType.APARTMENT), "apartment")
