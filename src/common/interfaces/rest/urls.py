# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

from src.common.interfaces.rest.views import PopularSearchesView

urlpatterns = [
    path("search/popular/", PopularSearchesView.as_view(), name="search-popular"),
]
