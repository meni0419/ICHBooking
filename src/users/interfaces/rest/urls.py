# Слой interfaces: маршрутизация текущего приложения
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, LogoutView, MeView, AddRoleView, RemoveRoleView, RefreshByCookieView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/refresh-by-cookie/", RefreshByCookieView.as_view(), name="auth-refresh-by-cookie"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/roles/add/", AddRoleView.as_view(), name="auth-role-add"),
    path("auth/roles/remove/", RemoveRoleView.as_view(), name="auth-role-remove"),
]
