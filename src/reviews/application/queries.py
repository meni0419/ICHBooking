# Слой application: запросы (чтение)
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ListReviewsForAccommodationQuery:
    accommodation_id: int

@dataclass(frozen=True)
class ListMyReviewsQuery:
    author_id: int