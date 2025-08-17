from __future__ import annotations

from datetime import date, timedelta

from src.bookings.domain.entities import BookingStatus, Booking
from src.bookings.domain.value_objects import StayPeriod


def make_booking(
        *,
        guest_id: int = 10,
        host_id: int = 20,
        start: date | None = None,
        end: date | None = None,
        status: BookingStatus = BookingStatus.REQUESTED,
) -> Booking:
    start = start or date.today() + timedelta(days=10)
    end = end or (start + timedelta(days=3))
    return Booking(
        id=None,
        accommodation_id=1,
        guest_id=guest_id,
        host_id=host_id,
        period=StayPeriod(start, end),
        status=status,
    )
