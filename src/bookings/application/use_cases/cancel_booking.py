from __future__ import annotations

from src.shared.errors import ApplicationError
from src.bookings.application.commands import CancelBookingCommand
from src.bookings.application.mappers import to_dto
from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.repository_interfaces import IBookingRepository


class CancelBookingUseCase:
    def __init__(self, repo: IBookingRepository):
        self._repo = repo

    def execute(self, cmd: CancelBookingCommand) -> BookingDTO:
        booking = self._repo.get_by_id(cmd.booking_id)
        if not booking:
            raise ApplicationError("Booking not found")
        try:
            booking.cancel(
                actor_user_id=cmd.actor_user_id,
                today=cmd.today,
                cancel_deadline_days=cmd.cancel_deadline_days,
            )
            saved = self._repo.update(booking)
            return to_dto(saved)
        except Exception as ex:
            raise ApplicationError(str(ex))