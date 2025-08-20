# Слой interfaces: DRF сериалайзеры
from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.users.domain.entities import UserRole


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    initial_role = serializers.ChoiceField(
        choices=[(UserRole.GUEST.value, "guest"), (UserRole.HOST.value, "host")],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError({"password_confirm": _("Passwords do not match")})
        return attrs


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    roles = serializers.ListField(child=serializers.CharField())


class RoleActionSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[(UserRole.GUEST.value, "guest"), (UserRole.HOST.value, "host")]
    )