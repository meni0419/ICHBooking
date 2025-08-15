# Слой domain: контракты репозиториев, абстрактные интерфейсы репозиториев (protocols/ABC)
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from .entities import Review


@runtime_checkable
class IReviewRepository(Protocol):
    """Контракт хранилища отзывов."""

    def get_by_id(self, review_id: int) -> Optional[Review]: ...

    def list_for_accommodation(self, accommodation_id: int) -> list[Review]: ...

    def list_by_author(self, author_id: int) -> list[Review]: ...

    def exists_for_booking(self, booking_id: int) -> bool: ...

    def create(self, review: Review) -> Review: ...

    def update(self, review: Review) -> Review: ...

    def delete(self, review_id: int, author_id: Optional[int] = None) -> None: ...
