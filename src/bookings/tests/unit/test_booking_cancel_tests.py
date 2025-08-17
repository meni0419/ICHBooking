from __future__ import annotations
from datetime import date, timedelta
from django.test import SimpleTestCase
from src.bookings.domain.entities import BookingStatus
from src.bookings.tests.factories import make_booking

class BookingCancelTests(SimpleTestCase):
    def test_guest_can_cancel_before_deadline(self):
        start = date.today() + timedelta(days=10)
        b = make_booking(start=start, end=start + timedelta(days=2), status=BookingStatus.REQUESTED)
        today = date.today()
        b.cancel(actor_user_id=b.guest_id, today=today, cancel_deadline_days=3)
        self.assertEqual(b.status, BookingStatus.CANCELLED)

    def test_guest_cannot_cancel_after_deadline(self):
        start = date.today() + timedelta(days=5)
        b = make_booking(start=start, end=start + timedelta(days=2), status=BookingStatus.CONFIRMED)
        # deadline: start - 3 дней; если сегодня > deadline -> ошибка
        today = start - timedelta(days=2)  # позже дедлайна на 1 день (если cancel_deadline_days=3)
        with self.assertRaises(ValueError):
            b.cancel(actor_user_id=b.guest_id, today=today, cancel_deadline_days=3)

    def test_host_can_cancel_before_start(self):
        start = date.today() + timedelta(days=2)
        b = make_booking(start=start, end=start + timedelta(days=3), status=BookingStatus.CONFIRMED)
        today = date.today()
        b.cancel(actor_user_id=b.host_id, today=today, cancel_deadline_days=3)
        self.assertEqual(b.status, BookingStatus.CANCELLED)

    def test_host_cannot_cancel_after_start(self):
        start = date.today()
        b = make_booking(start=start, end=start + timedelta(days=3), status=BookingStatus.REQUESTED)
        today = start  # уже началось
        with self.assertRaises(ValueError):
            b.cancel(actor_user_id=b.host_id, today=today, cancel_deadline_days=3)

    def test_third_party_cannot_cancel(self):
        b = make_booking(status=BookingStatus.REQUESTED)
        with self.assertRaises(PermissionError):
            b.cancel(actor_user_id=999, today=date.today(), cancel_deadline_days=3)

    def test_cannot_cancel_if_not_requested_or_confirmed(self):
        b = make_booking(status=BookingStatus.REJECTED)
        with self.assertRaises(ValueError):
            b.cancel(actor_user_id=b.guest_id, today=date.today(), cancel_deadline_days=3)
