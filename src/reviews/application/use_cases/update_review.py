from __future__ import annotations

from src.shared.errors import ApplicationError
from src.reviews.application.commands import UpdateReviewCommand
from src.reviews.application.mappers import to_dto
from src.reviews.domain.dtos import ReviewDTO
from src.reviews.domain.repository_interfaces import IReviewRepository
from src.reviews.domain.value_objects import Rating


class UpdateReviewUseCase:
    def __init__(self, reviews: IReviewRepository):
        self._reviews = reviews

    def execute(self, cmd: UpdateReviewCommand) -> ReviewDTO:
        review = self._reviews.get_by_id(cmd.review_id)
        if not review:
            raise ApplicationError("Review not found")
        if review.author_id != cmd.actor_user_id:
            raise ApplicationError("Not the author of the review")

        try:
            new_rating = Rating(cmd.rating) if cmd.rating is not None else None
            review.edit(new_rating=new_rating, new_text=cmd.text)
            saved = self._reviews.update(review)
            return to_dto(saved)
        except Exception as ex:
            raise ApplicationError(str(ex))