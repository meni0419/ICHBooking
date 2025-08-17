from django.urls import include, path

urlpatterns = [
    path('', include('src.reviews.interfaces.rest.urls')),
]
