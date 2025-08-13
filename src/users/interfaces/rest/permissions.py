# Слой interfaces: разрешения/доступ
from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsAuthenticatedAndActive(BasePermission):
    """
    Полезная базовая проверка: пользователь аутентифицирован и активен.
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "is_active", False))


class IsHost(BasePermission):
    """
    Доступ только пользователю, у которого есть роль 'host'.
    Ориентируемся на поле roles у ORM-модели пользователя (JSON-массив).
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not getattr(user, "is_active", False):
            return False
        roles = getattr(user, "roles", []) or []
        return "host" in roles


class IsGuest(BasePermission):
    """
    Доступ только пользователю, у которого есть роль 'guest'.
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not getattr(user, "is_active", False):
            return False
        roles = getattr(user, "roles", []) or []
        return "guest" in roles
