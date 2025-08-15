# Слой domain: сущности предметной области
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .value_objects import Rating


@dataclass
class Review:
    """Доменная сущность отзыва."""
    id: Optional[int]
    accommodation_id: int
    author_id: int  # guest
    booking_id: int
    rating: Rating
    text: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def edit(self, new_rating: Rating | None = None, new_text: str | None = None) -> None:
        if new_rating is not None:
            self.rating = new_rating
        if new_text is not None:
            t = (new_text or "").strip()
            if len(t) < 3:
                raise ValueError("Review text must be at least 3 characters")
            if len(t) > 5000:
                raise ValueError("Review text is too long")
            self.text = t

