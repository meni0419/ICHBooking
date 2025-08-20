# Django admin регистрации (инфраструктурный слой)
from django.contrib import admin

from .orm.models import Accommodation


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "owner_id", "city", "region", "price_cents", "rooms",
        "is_active", "views_count", "reviews_count", "average_rating", "created_at",
    )
    list_filter = ("is_active", "housing_type", "city", "region", "created_at")
    search_fields = ("title", "description", "city", "region")
    autocomplete_fields = ("owner",)
    ordering = ("-created_at",)
