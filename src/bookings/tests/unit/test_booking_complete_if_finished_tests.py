from __future__ import annotations
from datetime import date, timedelta
from django.test import SimpleTestCase
from src.bookings.domain.entities import BookingStatus
from src.bookings.tests.factories import make_booking

class BookingCompleteIfFinishedTests(SimpleTestCase):
    def test_complete_when_confirmed_and_finished(self):
        start = date.today() - timedelta(days=5)
        end = start + timedelta(days=2)  # уже закончилась
        b = make_booking(start=start, end=end, status=BookingStatus.CONFIRMED)
        b.complete_if_finished(today=date.today())
        self.assertEqual(b.status, BookingStatus.COMPLETED)

    def test_not_complete_if_not_confirmed(self):
        start = date.today() - timedelta(days=5)
        end = start + timedelta(days=2)
        b = make_booking(start=start, end=end, status=BookingStatus.REQUESTED)
        b.complete_if_finished(today=date.today())
        self.assertEqual(b.status, BookingStatus.REQUESTED)

    def test_not_complete_if_not_finished(self):
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=2)
        b = make_booking(start=start, end=end, status=BookingStatus.CONFIRMED)
        b.complete_if_finished(today=date.today())
        self.assertEqual(b.status, BookingStatus.CONFIRMED)
