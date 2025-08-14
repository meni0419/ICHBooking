from __future__ import annotations

from typing import List

from src.bookings.application.mappers import to_dto
from src.bookings.application.queries import ListMyBookingsQuery
from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.repository_interfaces import IBookingRepository


class ListMyBookingsUseCase:
    def __init__(self, repo: IBookingRepository):
        self._repo = repo

    def execute(self, q: ListMyBookingsQuery) -> List[BookingDTO]:
        bookings = self._repo.list_by_guest(guest_id=q.guest_id, active_only=q.active_only)
        return [to_dto(b) for b in bookings]
