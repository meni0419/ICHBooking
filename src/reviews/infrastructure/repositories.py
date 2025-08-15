# Слой infrastructure: реализации репозиториев (Django ORM), адаптеры для domain.repository_interfaces
from __future__ import annotations

from typing import Optional

from django.db.models import QuerySet

from src.reviews.domain.entities import Review as ReviewDomain
from src.reviews.domain.repository_interfaces import IReviewRepository
from src.reviews.domain.value_objects import Rating
from src.reviews.infrastructure.orm.models import Review as ReviewORM


def _to_domain(obj: ReviewORM) -> ReviewDomain:
    return ReviewDomain(
        id=obj.id,
        accommodation_id=obj.accommodation_id,
        author_id=obj.author_id,
        booking_id=obj.booking_id,
        rating=Rating(obj.rating),
        text=obj.text,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def _apply_domain(src: ReviewDomain, dst: ReviewORM) -> ReviewORM:
    dst.accommodation_id = src.accommodation_id
    dst.author_id = src.author_id
    dst.booking_id = src.booking_id
    dst.rating = src.rating.value
    dst.text = src.text
    return dst


class DjangoReviewRepository(IReviewRepository):
    def get_by_id(self, review_id: int) -> Optional[ReviewDomain]:
        try:
            return _to_domain(ReviewORM.objects.get(pk=review_id))
        except ReviewORM.DoesNotExist:
            return None

    def list_for_accommodation(self, accommodation_id: int) -> list[ReviewDomain]:
        qs: QuerySet[ReviewORM] = ReviewORM.objects.filter(accommodation_id=accommodation_id).order_by("-created_at")
        return [_to_domain(o) for o in qs]

    def list_by_author(self, author_id: int) -> list[ReviewDomain]:
        qs: QuerySet[ReviewORM] = ReviewORM.objects.filter(author_id=author_id).order_by("-created_at")
        return [_to_domain(o) for o in qs]

    def exists_for_booking(self, booking_id: int) -> bool:
        return ReviewORM.objects.filter(booking_id=booking_id).exists()

    def create(self, review: ReviewDomain) -> ReviewDomain:
        obj = ReviewORM()
        obj = _apply_domain(review, obj)
        obj.save()
        return _to_domain(obj)

    def update(self, review: ReviewDomain) -> ReviewDomain:
        obj = ReviewORM.objects.get(pk=review.id)
        obj = _apply_domain(review, obj)
        obj.save()
        return _to_domain(obj)

    def delete(self, review_id: int, author_id: Optional[int] = None) -> None:
        qs = ReviewORM.objects.filter(pk=review_id)
        if author_id is not None:
            qs = qs.filter(author_id=author_id)
        qs.delete()
