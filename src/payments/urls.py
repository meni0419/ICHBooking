from django.urls import include, path

urlpatterns = [
    path('api/', include('src.payments.interfaces.rest.urls')),
]
