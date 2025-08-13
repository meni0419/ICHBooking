from django.urls import include, path

urlpatterns = [
    path('api/', include('src.reviews.interfaces.rest.urls')),
]
