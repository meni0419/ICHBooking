from __future__ import annotations

from src.reviews.application.mappers import to_dto
from src.reviews.application.queries import ListReviewsForAccommodationQuery
from src.reviews.domain.dtos import ReviewDTO
from src.reviews.domain.repository_interfaces import IReviewRepository


class ListReviewsForAccommodationUseCase:
    def __init__(self, reviews: IReviewRepository):
        self._reviews = reviews

    def execute(self, q: ListReviewsForAccommodationQuery) -> list[ReviewDTO]:
        items = self._reviews.list_for_accommodation(q.accommodation_id)
        return [to_dto(r) for r in items]
