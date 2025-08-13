from django.urls import include, path

urlpatterns = [
    path('api/', include('src.bookings.interfaces.rest.urls')),
]
