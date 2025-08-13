# Django admin регистрации (инфраструктурный слой)
from django.contrib import admin

from .orm.models import Accommodation


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "city", "region", "price_cents", "rooms", "housing_type", "is_active", "owner", "created_at"
    )
    list_filter = ("is_active", "housing_type", "city", "region", "created_at")
    search_fields = ("title", "description", "city", "region")
    autocomplete_fields = ("owner",)
    ordering = ("-created_at",)