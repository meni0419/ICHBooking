# Слой domain: доменные сервисы (чистые функции/классы без инфраструктуры), доменные инварианты и бизнес-правила
from __future__ import annotations

from .entities import Review
from .value_objects import Rating


def create_review(
        *,
        accommodation_id: int,
        author_id: int,
        booking_id: int,
        rating: Rating,
        text: str,
        booking_belongs_to_author_and_accommodation: bool,
        booking_is_completed: bool,
        is_unique_for_booking: bool,

) -> Review:
    """
    Фабрика отзыва с доменными инвариантами:
    - отзыв может оставить только гость, у которого было завершённое бронирование данного объявления
      (флаг has_completed_stay — вычисляется в application-слое по бронированиям);
    - один отзыв на гостя и объявление (флаг is_unique_for_author — проверяется репозиторием в application-слое);
    - валидация рейтинга и текста.
    """
    if not booking_belongs_to_author_and_accommodation:
        raise ValueError("Booking does not belong to author/accommodation")
    if not booking_is_completed:
        raise ValueError("Booking must be completed to leave a review")
    if not is_unique_for_booking:
        raise ValueError("Review for this booking already exists")

    t = (text or "").strip()
    if len(t) < 10:
        raise ValueError("Review text must be at least 10 characters")
    if len(t) > 5000:
        raise ValueError("Review text is too long")

    return Review(
        id=None,
        accommodation_id=accommodation_id,
        author_id=author_id,
        booking_id=booking_id,
        rating=rating,
        text=t,
    )
