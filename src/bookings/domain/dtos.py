# Слой domain: DTO для обмена данными между слоями (без зависимостей от Django)
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .entities import BookingStatus


@dataclass
class BookingDTO:
    id: int
    accommodation_id: int
    guest_id: int
    host_id: int
    start_date: date
    end_date: date
    status: BookingStatus


@dataclass
class CreateBookingDTO:
    accommodation_id: int
    guest_id: int
    host_id: int
    start_date: date
    end_date: date