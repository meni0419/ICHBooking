from __future__ import annotations

from django.test import SimpleTestCase

from src.accommodations.domain.entities import Accommodation
from src.accommodations.domain.services import create_accommodation
from src.accommodations.domain.value_objects import Location, Price, RoomsCount, HousingType


class CreateAccommodationServiceTests(SimpleTestCase):
    def test_create_accommodation_success(self):
        acc = create_accommodation(
            owner_id=1,
            title="Nice flat",
            description="Cozy and clean apartment near center",
            location=Location(city="Berlin", region="Berlin", country="DE"),
            price=Price(amount_cents=15000),
            rooms=RoomsCount(2),
            housing_type=HousingType("apartment"),
            is_active=True,
        )
        self.assertIsInstance(acc, Accommodation)
        self.assertEqual(acc.owner_id, 1)
        self.assertEqual(acc.title, "Nice flat")
        self.assertEqual(acc.description, "Cozy and clean apartment near center")
        self.assertEqual(acc.location.city, "Berlin")
        self.assertEqual(acc.price.amount_cents, 15000)
        self.assertEqual(acc.rooms.value, 2)
        self.assertEqual(acc.housing_type.value if hasattr(acc.housing_type, "value") else acc.housing_type,
                         "apartment")
        self.assertTrue(acc.is_active)

    def test_create_accommodation_invalid_title(self):
        with self.assertRaises(ValueError):
            create_accommodation(
                owner_id=1,
                title="No",  # меньше 3-х символов — должен упасть
                description="Cozy and clean apartment near center",
                location=Location(city="Berlin", region="Berlin", country="DE"),
                price=Price(amount_cents=15000),
                rooms=RoomsCount(2),
                housing_type=HousingType("apartment"),
                is_active=True,
            )

    def test_create_accommodation_invalid_description(self):
        with self.assertRaises(ValueError):
            create_accommodation(
                owner_id=1,
                title="Nice flat",
                description="Too short",  # меньше 10 — должен упасть
                location=Location(city="Berlin", region="Berlin", country="DE"),
                price=Price(amount_cents=15000),
                rooms=RoomsCount(2),
                housing_type=HousingType("apartment"),
                is_active=True,
            )
