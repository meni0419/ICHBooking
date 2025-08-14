from __future__ import annotations

from typing import List

from src.bookings.application.mappers import to_dto
from src.bookings.application.queries import ListMyRequestsForHostQuery
from src.bookings.domain.dtos import BookingDTO
from src.bookings.domain.repository_interfaces import IBookingRepository


class ListMyRequestsForHostUseCase:
    def __init__(self, repo: IBookingRepository):
        self._repo = repo

    def execute(self, q: ListMyRequestsForHostQuery) -> List[BookingDTO]:
        bookings = self._repo.list_requests_for_host(host_id=q.host_id)
        return [to_dto(b) for b in bookings]