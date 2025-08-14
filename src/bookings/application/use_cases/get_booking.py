from __future__ import annotations

from src.shared.errors import ApplicationError
from src.bookings.application.mappers import to_dto
from src.bookings.application.queries import GetBookingByIdQuery
from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.repository_interfaces import IBookingRepository


class GetBookingByIdUseCase:
    def __init__(self, repo: IBookingRepository):
        self._repo = repo

    def execute(self, q: GetBookingByIdQuery) -> BookingDTO:
        booking = self._repo.get_by_id(q.booking_id)
        if not booking:
            raise ApplicationError("Booking not found")
        return to_dto(booking)
