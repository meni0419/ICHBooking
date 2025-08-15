# Слой infrastructure: Django ORM модели
from __future__ import annotations

from django.conf import settings
from django.db import models


class Review(models.Model):
    accommodation = models.ForeignKey(
        "accommodations.Accommodation",
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
    )
    booking = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="review",
        db_index=True,
    )

    rating = models.PositiveSmallIntegerField()
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        indexes = [
            models.Index(fields=["accommodation", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self) -> str:
        return f"Review#{self.pk} acc={self.accommodation_id} by={self.author_id} rating={self.rating}"
