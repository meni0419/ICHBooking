# Слой domain: доменные сервисы (чистые функции/классы без инфраструктуры), доменные инварианты и бизнес-правила
from __future__ import annotations

from datetime import date
from typing import Iterable

from .entities import Booking, BookingStatus
from .value_objects import StayPeriod


DEFAULT_CANCEL_DEADLINE_DAYS = 1  # гость может отменить не позднее чем за 1 день до начала


def ensure_no_overlaps(existing: Iterable[Booking], new_period: StayPeriod) -> None:
    """
    Проверка пересечений: запрещаем пересечения с CONFIRMED.
    Для простоты: блочим пересечения с CONFIRMED.
    """
    for b in existing:
        if b.status == BookingStatus.CONFIRMED and b.period.overlaps(new_period):
            raise ValueError("Booking overlaps with an existing confirmed booking")


def create_booking(
    *, accommodation_id: int, guest_id: int, host_id: int, period: StayPeriod, existing_for_acc: Iterable[Booking]
) -> Booking:
    """Фабрика бронирования с проверкой пересечений и начальными инвариантами."""
    ensure_no_overlaps(existing_for_acc, period)
    return Booking(
        id=None,
        accommodation_id=accommodation_id,
        guest_id=guest_id,
        host_id=host_id,
        period=period,
        status=BookingStatus.REQUESTED,
    )


def can_guest_review(guest_id: int, accommodation_id: int, bookings: Iterable[Booking], today: date) -> bool:
    """
    Политика для отзывов: гость может оставить отзыв, если у него было завершённое бронирование
    по этому объявлению с датой окончания < today (или статус COMPLETED).
    """
    for b in bookings:
        if (
            b.guest_id == guest_id
            and b.accommodation_id == accommodation_id
            and (b.status == BookingStatus.COMPLETED or today >= b.period.end_date)
        ):
            return True
    return False