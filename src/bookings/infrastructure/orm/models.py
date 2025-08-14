# Слой infrastructure: Django ORM модели
# Python
# src/bookings/infrastructure/orm/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    accommodation = models.ForeignKey(
        "accommodations.Accommodation",
        on_delete=models.CASCADE,
        related_name="bookings",
        db_index=True,
    )
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guest_bookings",
        db_index=True,
    )
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="host_bookings",
        db_index=True,
    )

    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookings"
        indexes = [
            models.Index(fields=["accommodation", "start_date", "end_date"]),
            models.Index(fields=["guest", "status"]),
            models.Index(fields=["host", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Booking#{self.pk} acc={self.accommodation_id} {self.start_date}->{self.end_date} {self.status}"
