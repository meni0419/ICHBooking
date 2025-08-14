# Слой application: команды (модифицирующие сценарии)
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreateBookingCommand:
    accommodation_id: int
    guest_id: int
    host_id: int
    start_date: date
    end_date: date


@dataclass(frozen=True)
class ConfirmBookingCommand:
    booking_id: int
    actor_user_id: int  # должен быть host


@dataclass(frozen=True)
class RejectBookingCommand:
    booking_id: int
    actor_user_id: int  # должен быть host


@dataclass(frozen=True)
class CancelBookingCommand:
    booking_id: int
    actor_user_id: int  # гость или хост
    today: date
    cancel_deadline_days: int = 1  # можно переопределить при необходимости
