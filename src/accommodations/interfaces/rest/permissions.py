# Слой interfaces: разрешения/доступ
from __future__ import annotations

from rest_framework.permissions import BasePermission
from src.common.interfaces.permissions import IsAuthenticatedAndActive

__all__ = ["IsAuthenticatedAndActive", "IsHost"]


class IsHost(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not getattr(user, "is_active", False):
            return False
        roles = getattr(user, "roles", []) or []
        return "host" in roles
