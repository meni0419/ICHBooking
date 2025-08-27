# Слой application: use case завершения бронирования
from __future__ import annotations

from src.shared.errors import ApplicationError
from src.bookings.application.commands import CompleteBookingCommand
from src.bookings.application.mappers import to_dto
from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.entities import BookingStatus
from src.bookings.domain.repository_interfaces import IBookingRepository


class CompleteBookingUseCase:
    def __init__(self, repo: IBookingRepository):
        self._repo = repo

    def execute(self, cmd: CompleteBookingCommand) -> BookingDTO:
        booking = self._repo.get_by_id(cmd.booking_id)
        if not booking:
            raise ApplicationError("Booking not found")

        # Предварительные проверки
        if booking.host_id != cmd.actor_user_id:
            raise ApplicationError("Forbidden")
        if booking.status != BookingStatus.CONFIRMED:
            raise ApplicationError("Only confirmed bookings can be completed")

        # Дата окончания берётся из value object period
        end_date = booking.period.end_date
        if cmd.today < end_date:
            raise ApplicationError("Booking cannot be completed before end_date")

        try:
            # Используем доменную логику
            booking.complete_if_finished(cmd.today)

            if booking.status != BookingStatus.COMPLETED:
                # На случай, если доменная логика не изменила статус (защита от несоответствий)
                raise ApplicationError("Booking could not be completed")

            saved = self._repo.update(booking)
            return to_dto(saved)
        except Exception as ex:
            raise ApplicationError(str(ex))
