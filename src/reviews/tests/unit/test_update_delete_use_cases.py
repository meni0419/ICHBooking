from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict

from django.test import SimpleTestCase

from src.shared.errors import ApplicationError
from src.reviews.domain.entities import Review
from src.reviews.domain.value_objects import Rating
from src.reviews.domain.repository_interfaces import IReviewRepository
from src.reviews.application.use_cases.update_review import UpdateReviewUseCase
from src.reviews.application.use_cases.delete_review import DeleteReviewUseCase
from src.reviews.application.use_cases.get_review import GetReviewUseCase
from src.reviews.application.commands import UpdateReviewCommand, DeleteReviewCommand, GetReviewCommand


class FakeReviewRepo(IReviewRepository):
    def __init__(self, seed: Optional[Review] = None):
        self._store: Dict[int, Review] = {}
        if seed:
            self._store[seed.id or 1] = Review(
                id=seed.id or 1,
                accommodation_id=seed.accommodation_id,
                author_id=seed.author_id,
                booking_id=seed.booking_id,
                rating=seed.rating,
                text=seed.text,
                created_at=seed.created_at,
                updated_at=seed.updated_at,
            )

    # IReviewRepository
    def get_by_id(self, review_id: int) -> Optional[Review]:
        return self._store.get(review_id)

    def list_for_accommodation(self, accommodation_id: int) -> list[Review]:
        return [r for r in self._store.values() if r.accommodation_id == accommodation_id]

    def list_by_author(self, author_id: int) -> list[Review]:
        return [r for r in self._store.values() if r.author_id == author_id]

    def exists_for_booking(self, booking_id: int) -> bool:
        return any(r.booking_id == booking_id for r in self._store.values())

    def create(self, review: Review) -> Review:
        new_id = max(self._store.keys() or [0]) + 1
        review.id = new_id
        self._store[new_id] = review
        return review

    def update(self, review: Review) -> Review:
        assert review.id in self._store
        self._store[review.id] = review
        return review

    def delete(self, review_id: int, author_id: Optional[int] = None) -> None:
        if review_id in self._store:
            if author_id is not None and self._store[review_id].author_id != author_id:
                return
            del self._store[review_id]


def make_seed_review() -> Review:
    return Review(
        id=1,
        accommodation_id=100,
        author_id=7,
        booking_id=77,
        rating=Rating(4),
        text="Seed text",
    )


class UpdateDeleteUseCasesTests(SimpleTestCase):
    def test_update_review_success(self):
        repo = FakeReviewRepo(make_seed_review())
        uc = UpdateReviewUseCase(reviews=repo)
        cmd = UpdateReviewCommand(review_id=1, actor_user_id=7, rating=5, text="Updated text")
        dto = uc.execute(cmd)
        self.assertEqual(dto.id, 1)
        self.assertEqual(dto.rating, 5)
        self.assertEqual(dto.text, "Updated text")

    def test_update_review_not_found(self):
        repo = FakeReviewRepo()
        uc = UpdateReviewUseCase(reviews=repo)
        cmd = UpdateReviewCommand(review_id=999, actor_user_id=7, rating=None, text="x")
        with self.assertRaises(ApplicationError):
            uc.execute(cmd)

    def test_update_review_not_author(self):
        repo = FakeReviewRepo(make_seed_review())
        uc = UpdateReviewUseCase(reviews=repo)
        cmd = UpdateReviewCommand(review_id=1, actor_user_id=999, rating=None, text="Another")
        with self.assertRaises(ApplicationError):
            uc.execute(cmd)

    def test_delete_review_success(self):
        repo = FakeReviewRepo(make_seed_review())
        uc = DeleteReviewUseCase(reviews=repo)
        cmd = DeleteReviewCommand(review_id=1, actor_user_id=7)
        uc.execute(cmd)
        self.assertIsNone(repo.get_by_id(1))

    def test_delete_review_not_found(self):
        repo = FakeReviewRepo()
        uc = DeleteReviewUseCase(reviews=repo)
        cmd = DeleteReviewCommand(review_id=1, actor_user_id=7)
        with self.assertRaises(ValueError):
            uc.execute(cmd)

    def test_get_review_success(self):
        repo = FakeReviewRepo(make_seed_review())
        uc = GetReviewUseCase(reviews=repo)
        dto = uc.execute(GetReviewCommand(review_id=1, actor_user_id=7))
        self.assertEqual(dto.id, 1)
        self.assertEqual(dto.text, "Seed text")

    def test_get_review_not_found(self):
        repo = FakeReviewRepo()
        uc = GetReviewUseCase(reviews=repo)
        with self.assertRaises(ApplicationError):
            uc.execute(GetReviewCommand(review_id=1, actor_user_id=7))

    def test_get_review_not_author(self):
        repo = FakeReviewRepo(make_seed_review())
        uc = GetReviewUseCase(reviews=repo)
        with self.assertRaises(ApplicationError):
            uc.execute(GetReviewCommand(review_id=1, actor_user_id=999))
