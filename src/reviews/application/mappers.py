# Python
from __future__ import annotations

from src.reviews.domain.dtos import ReviewDTO
from src.reviews.domain.entities import Review


def to_dto(r: Review) -> ReviewDTO:
    return ReviewDTO(
        id=r.id or 0,
        accommodation_id=r.accommodation_id,
        author_id=r.author_id,
        booking_id=r.booking_id,
        rating=r.rating.value,
        text=r.text,
        created_at=r.created_at,
    )