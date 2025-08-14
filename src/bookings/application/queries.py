# Слой application: запросы (чтение)
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetBookingByIdQuery:
    booking_id: int


@dataclass(frozen=True)
class ListMyBookingsQuery:
    guest_id: int
    active_only: bool = False


@dataclass(frozen=True)
class ListMyRequestsForHostQuery:
    host_id: int
