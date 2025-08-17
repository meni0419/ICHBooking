from __future__ import annotations
from django.test import SimpleTestCase
from src.bookings.domain.entities import BookingStatus
from src.bookings.tests.factories import make_booking

class BookingConfirmRejectTests(SimpleTestCase):
    def test_host_can_confirm_requested(self):
        b = make_booking(status=BookingStatus.REQUESTED)
        b.confirm(actor_user_id=b.host_id)
        self.assertEqual(b.status, BookingStatus.CONFIRMED)

    def test_guest_cannot_confirm(self):
        b = make_booking(status=BookingStatus.REQUESTED)
        with self.assertRaises(PermissionError):
            b.confirm(actor_user_id=b.guest_id)

    def test_confirm_only_from_requested(self):
        b = make_booking(status=BookingStatus.CONFIRMED)
        with self.assertRaises(ValueError):
            b.confirm(actor_user_id=b.host_id)

    def test_host_can_reject_requested(self):
        b = make_booking(status=BookingStatus.REQUESTED)
        b.reject(actor_user_id=b.host_id)
        self.assertEqual(b.status, BookingStatus.REJECTED)

    def test_guest_cannot_reject(self):
        b = make_booking(status=BookingStatus.REQUESTED)
        with self.assertRaises(PermissionError):
            b.reject(actor_user_id=b.guest_id)

    def test_reject_only_from_requested(self):
        b = make_booking(status=BookingStatus.CONFIRMED)
        with self.assertRaises(ValueError):
            b.reject(actor_user_id=b.host_id)
