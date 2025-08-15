# Слой domain: DTO для обмена данными между слоями (без зависимостей от Django)
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReviewDTO:
    id: int
    accommodation_id: int
    author_id: int
    booking_id: int
    rating: int
    text: str
    created_at: datetime


@dataclass
class CreateReviewDTO:
    """DTO для создания отзыва (на границе application)."""
    accommodation_id: int
    author_id: int
    booking_id: int
    rating: int  # 1..5
    text: str
