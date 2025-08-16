from __future__ import annotations

from django.test import SimpleTestCase

from src.reviews.domain.value_objects import Rating
from src.reviews.domain.services import create_review


class RatingValueObjectTests(SimpleTestCase):
    def test_rating_valid_bounds(self):
        self.assertEqual(Rating(1).value, 1)
        self.assertEqual(Rating(5).value, 5)

    def test_rating_invalid_bounds(self):
        with self.assertRaises(ValueError):
            Rating(0)
        with self.assertRaises(ValueError):
            Rating(6)


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

    def test_create_review_reject_if_booking_not_belongs(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="ok",
                booking_belongs_to_author_and_accommodation=False,
                booking_is_completed=True,
                is_unique_for_booking=True,
            )

    def test_create_review_reject_if_not_completed(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="ok",
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=False,
                is_unique_for_booking=True,
            )

    def test_create_review_reject_if_duplicate_for_booking(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="ok",
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=True,
                is_unique_for_booking=False,
            )

    def test_create_review_text_length_validation(self):
        with self.assertRaises(ValueError):
            create_review(
                accommodation_id=10,
                author_id=7,
                booking_id=77,
                rating=Rating(4),
                text="no",  # слишком короткий
                booking_belongs_to_author_and_accommodation=True,
                booking_is_completed=True,
                is_unique_for_booking=True,
            )