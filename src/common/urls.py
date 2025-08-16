from django.urls import include, path

urlpatterns = [
    path('', include('src.common.interfaces.rest.urls')),
]
