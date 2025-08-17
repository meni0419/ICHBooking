from __future__ import annotations

from django.test import SimpleTestCase

from src.reviews.domain.entities import Review
from src.reviews.domain.value_objects import Rating


def make_review() -> Review:
    return Review(
        id=None,
        accommodation_id=100,
        author_id=7,
        booking_id=77,
        rating=Rating(4),
        text="Initial valid text",
    )


class ReviewEntityTests(SimpleTestCase):
    def test_edit_update_rating_and_text(self):
        r = make_review()
        r.edit(new_rating=Rating(5), new_text="Updated valid text")
        self.assertEqual(r.rating.value, 5)
        self.assertEqual(r.text, "Updated valid text")

    def test_edit_text_too_short(self):
        r = make_review()
        with self.assertRaises(ValueError):
            r.edit(new_text="no")

    def test_edit_text_too_long(self):
        r = make_review()
        with self.assertRaises(ValueError):
            r.edit(new_text="x" * 5001)

    def test_edit_rating_only(self):
        r = make_review()
        r.edit(new_rating=Rating(3))
        self.assertEqual(r.rating.value, 3)
        self.assertEqual(r.text, "Initial valid text")

    def test_edit_text_only(self):
        r = make_review()
        r.edit(new_text="Text changed only")
        self.assertEqual(r.text, "Text changed only")
        self.assertEqual(r.rating.value, 4)
