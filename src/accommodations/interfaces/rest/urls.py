# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

from src.reviews.interfaces.rest.views import ListReviewsForAccommodationView
from .views import (
    CreateAccommodationView, ToggleAvailabilityView,
    AccommodationDetailView, ListMyAccommodationsView, SearchAccommodationsView,
)

urlpatterns = [
    path("", CreateAccommodationView.as_view(), name="accommodations-create"),  # POST
    path("mine/", ListMyAccommodationsView.as_view(), name="accommodations-mine"),  # GET
    path("search/", SearchAccommodationsView.as_view(), name="accommodations-search"),  # GET
    path("<int:acc_id>/", AccommodationDetailView.as_view(), name="accommodations-detail"),  # GET/PATCH/DELETE
    path("<int:accommodation_id>/reviews/", ListReviewsForAccommodationView.as_view(), name="accommodations-reviews"),
    path("<int:acc_id>/toggle/", ToggleAvailabilityView.as_view(), name="accommodations-toggle"),  # POST
]
