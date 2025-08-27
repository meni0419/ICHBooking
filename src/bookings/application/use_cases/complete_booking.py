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

        # Предварительные проверки на уровне use case (дублируют доменную защиту)
        if booking.host_id != cmd.actor_user_id:
            # Хост может завершать только свои бронирования
            raise ApplicationError("Forbidden")
        if booking.status != BookingStatus.CONFIRMED:
            # Завершать можно только подтверждённые брони
            raise ApplicationError("Only confirmed bookings can be completed")
        if cmd.today < booking.end_date:
            # Дата окончания должна уже наступить (сегодня или в прошлом)
            raise ApplicationError("Booking cannot be completed before end_date")

        try:
            # Если в домене есть метод complete — используем его, чтобы соблюсти инварианты
            if hasattr(booking, "complete") and callable(getattr(booking, "complete")):
                booking.complete(actor_user_id=cmd.actor_user_id, today=cmd.today)
            else:
                # Фолбэк: проставляем статус напрямую, инварианты уже проверены выше
                booking.status = BookingStatus.COMPLETED

            saved = self._repo.update(booking)
            return to_dto(saved)
        except Exception as ex:
            raise ApplicationError(str(ex))