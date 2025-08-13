from django.urls import include, path

urlpatterns = [
    path('api/', include('src.accommodations.interfaces.rest.urls')),
]
