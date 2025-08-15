from __future__ import annotations

from src.reviews.application.commands import DeleteReviewCommand
from src.reviews.domain.repository_interfaces import IReviewRepository


class DeleteReviewUseCase:
    def __init__(self, reviews: IReviewRepository):
        self._reviews = reviews

    def execute(self, cmd: DeleteReviewCommand) -> None:

        review = self._reviews.get_by_id(cmd.review_id)
        if not review:
            raise ValueError("Review not found")

        if review.author_id != cmd.actor_user_id:
            raise ValueError("Not the author of the review")

        self._reviews.delete(cmd.review_id, author_id=cmd.actor_user_id)
