from django.urls import include, path

urlpatterns = [
    path('api/', include('src.users.interfaces.rest.urls')),
]
