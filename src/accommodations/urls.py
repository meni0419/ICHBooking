from django.urls import include, path

urlpatterns = [
    path('', include('src.accommodations.interfaces.rest.urls')),
]
