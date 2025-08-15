# Слой application: команды (модифицирующие сценарии)
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateReviewCommand:
    accommodation_id: int
    author_id: int
    booking_id: int
    rating: int
    text: str


@dataclass(frozen=True)
class UpdateReviewCommand:
    review_id: int
    actor_user_id: int
    rating: Optional[int] = None
    text: Optional[str] = None


@dataclass(frozen=True)
class DeleteReviewCommand:
    review_id: int
    actor_user_id: int
