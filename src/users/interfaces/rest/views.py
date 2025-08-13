# src/users/interfaces/rest/views.py
from __future__ import annotations

import os
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from src.users.interfaces.rest.serializers import (
    RegisterSerializer,
    UserSerializer,
    RoleActionSerializer,
)
from src.users.application.commands import RegisterUserCommand, AddRoleCommand, RemoveRoleCommand
from src.users.application.queries import GetCurrentUserQuery
from src.users.application.use_cases.register_user import RegisterUserUseCase
from src.users.application.use_cases.get_current_user import GetCurrentUserUseCase
from src.users.application.use_cases.assign_roles import AddRoleUseCase, RemoveRoleUseCase
from src.users.application.ports import IAuthProvider
from src.users.domain.entities import UserRole
from src.users.domain.value_objects import Email
from src.users.infrastructure.repositories import DjangoUserRepository
from src.users.infrastructure.auth_provider import DjangoAuthProvider


def _get_jwt_cookie_names():
    access_name = os.getenv("JWT_ACCESS_COOKIE_NAME", "access_token")
    refresh_name = os.getenv("JWT_REFRESH_COOKIE_NAME", "refresh_token")
    return access_name, refresh_name


def _get_cookie_flags():
    secure = settings.SECURE_COOKIES
    samesite = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
    return secure, samesite


def _set_jwt_cookies(response: Response, access_token: str, refresh_token: Optional[str] = None):
    access_name, refresh_name = _get_jwt_cookie_names()
    secure, samesite = _get_cookie_flags()

    access_max_age = int(timedelta(minutes=int(os.getenv("JWT_ACCESS_LIFETIME_MIN", "15"))).total_seconds())
    refresh_max_age = int(timedelta(days=int(os.getenv("JWT_REFRESH_LIFETIME_DAYS", "7"))).total_seconds())

    if access_token:
        response.set_cookie(
            key=access_name,
            value=access_token,
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=access_max_age,
            path="/",
        )
    if refresh_token:
        response.set_cookie(
            key=refresh_name,
            value=refresh_token,
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=refresh_max_age,
            path="/",
        )


def _clear_jwt_cookies(response: Response):
    access_name, refresh_name = _get_jwt_cookie_names()
    response.delete_cookie(access_name, path="/")
    response.delete_cookie(refresh_name, path="/")


@extend_schema(
    request=RegisterSerializer,
    responses={201: UserSerializer},
    tags=["auth"],
    operation_id="auth_register",
    description="Регистрация пользователя. Требуется CSRF (см. /api/csrf/ и Authorize->csrf).",
)
@method_decorator(csrf_protect, name="dispatch")
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        users_repo = DjangoUserRepository()
        auth_provider: IAuthProvider = DjangoAuthProvider()
        initial_role_raw: Optional[str] = serializer.validated_data.get("initial_role") or None
        initial_roles = [UserRole(initial_role_raw)] if initial_role_raw else None

        use_case = RegisterUserUseCase(users=users_repo, auth=auth_provider)
        dto = use_case.execute(
            RegisterUserCommand(
                name=serializer.validated_data["name"],
                email=Email(serializer.validated_data["email"]),
                password=serializer.validated_data["password"],
                password_confirm=serializer.validated_data["password_confirm"],
                initial_roles=initial_roles,
            )
        )
        return Response(UserSerializer(dto).data, status=status.HTTP_201_CREATED)


@extend_schema(
    request={"application/json": {"type": "object", "properties": {"email": {"type": "string"}, "password": {"type": "string"}}}},
    responses={200: OpenApiResponse(description="Login successful (JWT cookies set)")},
    tags=["auth"],
    operation_id="auth_login",
    description="Логин. Устанавливает JWT в HttpOnly куки.",
)
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            tokens = response.data
            access = tokens.get("access")
            refresh = tokens.get("refresh")
            response.data = {"detail": "Login successful"}
            if access and refresh:
                _set_jwt_cookies(response, access, refresh)
        return response


@extend_schema(
    responses={200: OpenApiResponse(description="Access token refreshed (cookies updated)")},
    tags=["auth"],
    operation_id="auth_refresh_by_cookie",
    description="Обновляет access (и при ротации — refresh) по refresh-токену из куки. Требуется CSRF.",
)
@method_decorator(csrf_protect, name="dispatch")
class RefreshByCookieView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        _, refresh_name = _get_jwt_cookie_names()
        refresh_cookie = request.COOKIES.get(refresh_name)
        if not refresh_cookie:
            return Response({"detail": "Refresh cookie not found"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenRefreshSerializer(data={"refresh": refresh_cookie})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data  # {'access': '...', 'refresh': '...'(optional when rotation enabled)}

        resp = Response({"detail": "Refreshed"}, status=status.HTTP_200_OK)
        new_access = data.get("access")
        new_refresh = data.get("refresh")
        _set_jwt_cookies(resp, access_token=new_access, refresh_token=new_refresh)
        return resp


@extend_schema(
    responses={200: OpenApiResponse(description="Logged out (cookies cleared)")},
    tags=["auth"],
    operation_id="auth_logout",
    description="Логаут. Очищает куки и отправляет refresh в blacklist.",
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            _, refresh_name = _get_jwt_cookie_names()
            refresh_token = request.COOKIES.get(refresh_name)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        resp = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        _clear_jwt_cookies(resp)
        return resp


@extend_schema(responses={200: UserSerializer}, tags=["auth"], operation_id="auth_me")
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users_repo = DjangoUserRepository()
        use_case = GetCurrentUserUseCase(users=users_repo)
        dto = use_case.execute(GetCurrentUserQuery(user_id=request.user.id))
        return Response(UserSerializer(dto).data, status=status.HTTP_200_OK)


@extend_schema(request=RoleActionSerializer, responses={200: UserSerializer}, tags=["auth"], operation_id="auth_role_add")
class AddRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = RoleActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        role = UserRole(ser.validated_data["role"])

        users_repo = DjangoUserRepository()
        use_case = AddRoleUseCase(users=users_repo)
        dto = use_case.execute(AddRoleCommand(user_id=request.user.id, role=role))
        return Response(UserSerializer(dto).data, status=status.HTTP_200_OK)


@extend_schema(request=RoleActionSerializer, responses={200: UserSerializer}, tags=["auth"], operation_id="auth_role_remove")
class RemoveRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = RoleActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        role = UserRole(ser.validated_data["role"])

        users_repo = DjangoUserRepository()
        use_case = RemoveRoleUseCase(users=users_repo)
        dto = use_case.execute(RemoveRoleCommand(user_id=request.user.id, role=role))
        return Response(UserSerializer(dto).data, status=status.HTTP_200_OK)