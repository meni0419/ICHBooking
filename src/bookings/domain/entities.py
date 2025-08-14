# Слой domain: сущности предметной области
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum, unique
from typing import Optional

from .value_objects import StayPeriod


@unique
class BookingStatus(Enum):
    REQUESTED = "requested"  # заявка гостя, ожидает решения хоста
    CONFIRMED = "confirmed"  # подтверждено хостом
    REJECTED = "rejected"  # отклонено хостом
    CANCELLED = "cancelled"  # отменено гостем/хостом по правилам
    COMPLETED = "completed"  # завершено (по окончании проживания)


@dataclass
class Booking:
    id: Optional[int]
    accommodation_id: int
    guest_id: int
    host_id: int
    period: StayPeriod
    status: BookingStatus = BookingStatus.REQUESTED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def confirm(self, actor_user_id: int) -> None:
        if actor_user_id != self.host_id:
            raise PermissionError("Only host can confirm booking")
        if self.status != BookingStatus.REQUESTED:
            raise ValueError("Only requested booking can be confirmed")
        self.status = BookingStatus.CONFIRMED

    def reject(self, actor_user_id: int) -> None:
        if actor_user_id != self.host_id:
            raise PermissionError("Only host can reject booking")
        if self.status != BookingStatus.REQUESTED:
            raise ValueError("Only requested booking can be rejected")
        self.status = BookingStatus.REJECTED

    def cancel(self, actor_user_id: int, today: date, cancel_deadline_days: int) -> None:
        """
        Отмена допускается:
        - Гостем до дедлайна (today <= start - cancel_deadline_days)
        - Хостом — пока статус REQUESTED/CONFIRMED (правило уточняется политикой)
        """
        if self.status not in (BookingStatus.REQUESTED, BookingStatus.CONFIRMED):
            raise ValueError("Only requested/confirmed booking can be cancelled")
        # Хост может отменить в любой момент до начала (простая политика)
        if actor_user_id == self.host_id:
            if today >= self.period.start_date:
                raise ValueError("Host cannot cancel after start date")
            self.status = BookingStatus.CANCELLED
            return
        # Гость — до дедлайна
        if actor_user_id == self.guest_id:
            deadline = self.period.start_date
            # today <= start_date - cancel_deadline_days
            from datetime import timedelta
            if today > (deadline - timedelta(days=cancel_deadline_days)):
                raise ValueError("Guest cannot cancel after deadline")
            self.status = BookingStatus.CANCELLED
            return
        raise PermissionError("Only guest or host can cancel booking")

    def complete_if_finished(self, today: date) -> None:
        """Помечает как завершённое, если период истёк."""
        if self.status == BookingStatus.CONFIRMED and today >= self.period.end_date:
            self.status = BookingStatus.COMPLETED
