# Django admin регистрации (инфраструктурный слой)
from django.contrib import admin

from .orm.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "accommodation", "author", "booking", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("text", "accommodation__title", "author__email")
    autocomplete_fields = ("accommodation", "author", "booking")
    ordering = ("-created_at",)
