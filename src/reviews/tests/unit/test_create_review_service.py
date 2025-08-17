from __future__ import annotations

from django.test import SimpleTestCase

from src.reviews.domain.value_objects import Rating
from src.reviews.domain.services import create_review


class CreateReviewServiceTests(SimpleTestCase):
    def test_create_review_success(self):
        r = create_review(
            accommodation_id=10,
            author_id=7,
            booking_id=77,
            rating=Rating(5),
            text="Great place, thanks!",
            booking_belongs_to_author_and_accommodation=True,
            booking_is_completed=True,
            is_unique_for_booking=True,
        )
        self.assertEqual(r.accommodation_id, 10)
        self.assertEqual(r.author_id, 7)
        self.assertEqual(r.booking_id, 77)
        self.assertEqual(r.rating.value, 5)
        self.assertEqual(r.text, "Great place, thanks!")

    def test_reject_if_booking_not_belongs(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="This is a valid length text",
                booking_belongs_to_author_and_accommodation=False,
                booking_is_completed=True,
                is_unique_for_booking=True,
            )

    def test_reject_if_not_completed(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="This is a valid length text",
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=False,
                is_unique_for_booking=True,
            )

    def test_reject_if_duplicate_for_booking(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="This is a valid length text",
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=True,
                is_unique_for_booking=False,
            )

    def test_text_length_validation_min(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="short",
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=True,
                is_unique_for_booking=True,
            )

    def test_text_length_validation_max(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="x" * 5001,
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=True,
                is_unique_for_booking=True,
            )