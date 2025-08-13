from django.urls import include, path

urlpatterns = [
    path('', include('src.users.interfaces.rest.urls')),
]
