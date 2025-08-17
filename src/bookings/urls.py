from django.urls import include, path

urlpatterns = [
    path('', include('src.bookings.interfaces.rest.urls')),
]
