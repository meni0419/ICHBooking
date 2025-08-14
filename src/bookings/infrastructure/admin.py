# Django admin регистрации (инфраструктурный слой)
from django.contrib import admin

from .orm.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "accommodation", "guest", "host", "start_date", "end_date", "status", "created_at")
    list_filter = ("status", "start_date", "end_date", "created_at")
    search_fields = ("accommodation__title", "guest__email", "host__email")
    autocomplete_fields = ("accommodation", "guest", "host")
    ordering = ("-created_at",)