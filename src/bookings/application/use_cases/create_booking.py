from __future__ import annotations

from src.shared.errors import ApplicationError
from src.bookings.application.commands import CreateBookingCommand
from src.bookings.application.mappers import to_dto
from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.repository_interfaces import IBookingRepository
from src.bookings.domain.services import create_booking
from src.bookings.domain.value_objects import StayPeriod


class CreateBookingUseCase:
    def __init__(self, repo: IBookingRepository):
        self._repo = repo

    def execute(self, cmd: CreateBookingCommand) -> BookingDTO:
        try:
            period = StayPeriod(start_date=cmd.start_date, end_date=cmd.end_date)
            existing = self._repo.find_overlaps(cmd.accommodation_id, period)
            entity = create_booking(
                accommodation_id=cmd.accommodation_id,
                guest_id=cmd.guest_id,
                host_id=cmd.host_id,
                period=period,
                existing_for_acc=existing,
            )
            created = self._repo.create(entity)
            return to_dto(created)
        except ApplicationError:
            raise
        except Exception as ex:
            raise ApplicationError(str(ex))