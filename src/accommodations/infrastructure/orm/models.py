# Слой infrastructure: Django модели ORM, связанные с domain через маппинг
from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models


class Accommodation(models.Model):
    class HousingTypes(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        STUDIO = "studio", "Studio"
        ROOM = "room", "Room"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accommodations",
        db_index=True,
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    # Локация
    city = models.CharField(max_length=120, db_index=True)
    region = models.CharField(max_length=120, db_index=True)
    country = models.CharField(max_length=2, default="DE")
    # Цена и параметры
    price_cents = models.PositiveIntegerField(db_index=True)
    rooms = models.PositiveSmallIntegerField()
    housing_type = models.CharField(max_length=20, choices=HousingTypes.choices, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    impressions_count = models.BigIntegerField(default=0, db_index=True)
    views_count = models.BigIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "accommodations"
        indexes = [
            models.Index(fields=["is_active", "price_cents"]),
            models.Index(fields=["city", "region"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.city}, {self.region})"
