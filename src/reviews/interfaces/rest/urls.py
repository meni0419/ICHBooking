# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

from .views import (
    CreateReviewView,
    ListReviewsForAccommodationView,
    ListMyReviewsView,
    GetUpdateDeleteReviewView,
)

urlpatterns = [
    path("", CreateReviewView.as_view(), name="reviews-create"),  # POST
    path("mine/", ListMyReviewsView.as_view(), name="reviews-mine"),  # GET
    path("accommodations/<int:accommodation_id>/", ListReviewsForAccommodationView.as_view(),
         name="reviews-for-accommodation"),  # GET
    path("<int:review_id>/", GetUpdateDeleteReviewView.as_view(), name="reviews-get-update-delete"),  # GET/PATCH/DELETE
]
