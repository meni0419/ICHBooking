from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from src.common.interfaces.rest.views import CsrfCookieView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Схема и Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Утилита CSRF
    path("api/csrf/", CsrfCookieView.as_view(), name="csrf-cookie"),
    # Роуты приложений
    path("api/users/", include("src.users.urls")),
    path("api/accommodations/", include("src.accommodations.urls")),
    path("api/bookings/", include("src.bookings.urls")),
    path("api/reviews/", include("src.reviews.urls")),
]
