from __future__ import annotations

from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.entities import Booking


def to_dto(b: Booking) -> BookingDTO:
    return BookingDTO(
        id=b.id or 0,
        accommodation_id=b.accommodation_id,
        guest_id=b.guest_id,
        host_id=b.host_id,
        start_date=b.period.start_date,
        end_date=b.period.end_date,
        status=b.status,
    )