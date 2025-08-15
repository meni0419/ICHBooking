from __future__ import annotations

from src.reviews.application.mappers import to_dto
from src.reviews.application.queries import ListMyReviewsQuery
from src.reviews.domain.dtos import ReviewDTO
from src.reviews.domain.repository_interfaces import IReviewRepository


class ListMyReviewsUseCase:
    def __init__(self, reviews: IReviewRepository):
        self._reviews = reviews

    def execute(self, q: ListMyReviewsQuery) -> list[ReviewDTO]:
        items = self._reviews.list_by_author(q.author_id)
        return [to_dto(r) for r in items]
