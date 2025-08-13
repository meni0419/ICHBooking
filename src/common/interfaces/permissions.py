from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActive(BasePermission):
    """Пользователь аутентифицирован и активен."""
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "is_active", False))