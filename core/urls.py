from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Схема и Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Роуты приложений
    path("api/users/", include("src.users.urls")),
    path("api/accommodations/", include("src.accommodations.urls")),
    path("api/bookings/", include("src.bookings.urls")),
    path("api/reviews/", include("src.reviews.urls")),
]
