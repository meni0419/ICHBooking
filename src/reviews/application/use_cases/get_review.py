from __future__ import annotations

from src.shared.errors import ApplicationError
from src.reviews.application.commands import GetReviewCommand
from src.reviews.application.mappers import to_dto
from src.reviews.domain.dtos import ReviewDTO
from src.reviews.domain.repository_interfaces import IReviewRepository


class GetReviewUseCase:
    def __init__(self, reviews: IReviewRepository):
        self._reviews = reviews

    def execute(self, cmd: GetReviewCommand) -> ReviewDTO:
        review = self._reviews.get_by_id(cmd.review_id)
        if not review:
            raise ApplicationError("Review not found")
        if review.author_id != cmd.actor_user_id:
            raise ApplicationError("Not the author of the review")
        return to_dto(review)
