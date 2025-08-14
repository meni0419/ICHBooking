# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

from .views import (
    CreateBookingView,
    ListMyBookingsView,
    ListMyRequestsForHostView,
    ConfirmBookingView,
    RejectBookingView,
    CancelBookingView, BookingDetailView,
)

urlpatterns = [
    path("", CreateBookingView.as_view(), name="bookings-create"),  # POST
    path("me/", ListMyBookingsView.as_view(), name="bookings-me"),  # GET
    path("requests/", ListMyRequestsForHostView.as_view(), name="bookings-requests"),  # GET
    path("<int:booking_id>/", BookingDetailView.as_view(), name="bookings-detail"),  # GET
    path("<int:booking_id>/confirm/", ConfirmBookingView.as_view(), name="bookings-confirm"),  # POST
    path("<int:booking_id>/reject/", RejectBookingView.as_view(), name="bookings-reject"),    # POST
    path("<int:booking_id>/cancel/", CancelBookingView.as_view(), name="bookings-cancel"),    # POST
]
