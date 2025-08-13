from django.urls import include, path

urlpatterns = [
    path('api/', include('src.common.interfaces.rest.urls')),
]
