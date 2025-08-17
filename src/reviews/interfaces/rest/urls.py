# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

from .views import (
    CreateReviewView,
    ListMyReviewsView,
    GetUpdateDeleteReviewView,
)

urlpatterns = [
    path("", CreateReviewView.as_view(), name="reviews-create"),  # POST
    path("me/", ListMyReviewsView.as_view(), name="reviews-me"),  # GET
    path("<int:review_id>/", GetUpdateDeleteReviewView.as_view(), name="reviews-get-update-delete"),  # GET/PATCH/DELETE
]
