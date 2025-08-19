# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

from .views import (
    ListMyReviewsView,
    ListReviewsByUserIdView,
    GetUpdateDeleteReviewView,
)

urlpatterns = [

    path("me/", ListMyReviewsView.as_view(), name="reviews-me"),  # GET
    path("user/<int:user_id>/", ListReviewsByUserIdView.as_view(), name="reviews-user"),
    path("<int:review_id>/", GetUpdateDeleteReviewView.as_view(), name="reviews-get-update-delete"),  # GET/PATCH/DELETE
]
