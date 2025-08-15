from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import debug_toolbar
from django.conf import settings

from src.common.interfaces.rest.views import CsrfCookieView


urlpatterns = [
    path("admin/", admin.site.urls),
    # Схема и Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(),
         name="swagger-ui"),
    # path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema", template_name="swagger_ui_dark.html"),name="swagger-ui"),
    # Утилита CSRF
    path("api/csrf/", CsrfCookieView.as_view(), name="csrf-cookie"),
    # Роуты приложений
    path("api/users/", include("src.users.urls")),
    path("api/accommodations/", include("src.accommodations.urls")),
    path("api/bookings/", include("src.bookings.urls")),
    path("api/reviews/", include("src.reviews.urls")),
    path("api/common/", include("src.common.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls))
    ]
