# Слой infrastructure: реализации репозиториев (Django ORM), адаптеры для domain.repository_interfaces
from __future__ import annotations

from datetime import date
from typing import Optional

from django.db.models import Q

from src.bookings.domain.entities import Booking as BookingDomain, BookingStatus
from src.bookings.domain.repository_interfaces import IBookingRepository
from src.bookings.domain.value_objects import StayPeriod
from src.bookings.infrastructure.orm.models import Booking as BookingORM


def _to_domain(obj: BookingORM) -> BookingDomain:
    return BookingDomain(
        id=obj.id,
        accommodation_id=obj.accommodation_id,
        guest_id=obj.guest_id,
        host_id=obj.host_id,
        period=StayPeriod(start_date=obj.start_date, end_date=obj.end_date),
        status=BookingStatus(obj.status),
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


def _apply_domain(src: BookingDomain, dst: BookingORM) -> BookingORM:
    dst.accommodation_id = src.accommodation_id
    dst.guest_id = src.guest_id
    dst.host_id = src.host_id
    dst.start_date = src.period.start_date
    dst.end_date = src.period.end_date
    dst.status = src.status.value
    return dst


class DjangoBookingRepository(IBookingRepository):
    def get_by_id(self, booking_id: int) -> Optional[BookingDomain]:
        try:
            return _to_domain(BookingORM.objects.get(pk=booking_id))
        except BookingORM.DoesNotExist:
            return None

    def create(self, booking: BookingDomain) -> BookingDomain:
        obj = BookingORM()
        obj = _apply_domain(booking, obj)
        obj.save()
        return _to_domain(obj)

    def update(self, booking: BookingDomain) -> BookingDomain:
        obj = BookingORM.objects.get(pk=booking.id)
        obj = _apply_domain(booking, obj)
        obj.save()
        return _to_domain(obj)

    def list_by_guest(self, guest_id: int, active_only: bool = False) -> list[BookingDomain]:
        qs = BookingORM.objects.filter(guest_id=guest_id)
        if active_only:
            qs = qs.filter(status__in=[BookingORM.Status.REQUESTED, BookingORM.Status.CONFIRMED])
        return [_to_domain(o) for o in qs.order_by("-created_at")]

    def list_requests_for_host(self, host_id: int) -> list[BookingDomain]:
        qs = BookingORM.objects.filter(host_id=host_id, status=BookingORM.Status.REQUESTED)
        return [_to_domain(o) for o in qs.order_by("start_date", "id")]

    def list_for_accommodation_confirmed(self, accommodation_id: int) -> list[BookingDomain]:
        qs = BookingORM.objects.filter(
            accommodation_id=accommodation_id, status=BookingORM.Status.CONFIRMED
        )
        return [_to_domain(o) for o in qs.order_by("start_date", "id")]

    def find_overlaps(
            self, accommodation_id: int, period: StayPeriod, exclude_booking_id: Optional[int] = None
    ) -> list[BookingDomain]:
        """
        Пересечение полуинтервалов [start, end):
          NOT (end <= start2 OR end2 <= start)
        """
        qs = BookingORM.objects.filter(accommodation_id=accommodation_id)
        # Опционально исключим текущую бронь
        if exclude_booking_id is not None:
            qs = qs.exclude(pk=exclude_booking_id)

        # Формула пересечения
        overlaps_filter = Q(end_date__gt=period.start_date) & Q(start_date__lt=period.end_date)
        qs = qs.filter(overlaps_filter)
        return [_to_domain(o) for o in qs]

    def list_in_period_for_guest(self, guest_id: int, start: date, end: date) -> list[BookingDomain]:
        qs = BookingORM.objects.filter(
            guest_id=guest_id,
            end_date__gt=start,
            start_date__lt=end,
        )
        return [_to_domain(o) for o in qs.order_by("start_date", "id")]
