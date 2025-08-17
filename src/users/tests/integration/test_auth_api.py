from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient

from src.shared.testing.api import ensure_csrf
from src.shared.testing.factories import create_user


class UsersAuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success_guest_by_default(self):
        headers = ensure_csrf(self.client)
        payload = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "secret123",
            "password_confirm": "secret123",
            # initial_role опционален — по умолчанию guest
        }
        resp = self.client.post("/api/users/auth/register/", payload, format="json", **headers)
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data["email"], "newuser@example.com")
        # гость по умолчанию
        # roles может быть списком строк или enum-подобных значений — проверим по включению "guest"
        roles = data.get("roles") or []
        self.assertTrue(any(str(r).endswith("guest") or str(r) == "guest" for r in roles), roles)

    def test_login_sets_jwt_cookies(self):
        # создаём пользователя с паролем
        user = create_user("login-user@example.com", password="pass123", roles=["guest"])
        resp = self.client.post(
            "/api/users/auth/login/",
            {"email": "login-user@example.com", "password": "pass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        # Проверим, что Set-Cookie содержит access_token/refresh_token (имена по умолчанию)
        set_cookie_header = "; ".join(resp.cookies.keys())
        self.assertIn("access_token", set_cookie_header)
        self.assertIn("refresh_token", set_cookie_header)

    def test_me_requires_auth_and_returns_user(self):
        # без аутентификации
        resp = self.client.get("/api/users/auth/me/")
        self.assertIn(resp.status_code, (401, 403), resp.content)

        # с аутентификацией (force_authenticate)
        user = create_user("me-user@example.com", roles=["guest"])
        self.client.force_authenticate(user=user)
        resp = self.client.get("/api/users/auth/me/")
        self.assertEqual(resp.status_code, 200, resp.content)
        data = resp.json()
        self.assertEqual(data["email"], "me-user@example.com")

    def test_add_and_remove_roles(self):
        user = create_user("roles-user@example.com", roles=["guest"])
        self.client.force_authenticate(user=user)

        # Добавляем host
        resp = self.client.post("/api/users/auth/roles/add/", {"role": "host"}, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)
        roles = resp.json().get("roles") or []
        self.assertTrue(any(str(r).endswith("host") or str(r) == "host" for r in roles), roles)

        # Убираем guest
        resp = self.client.post("/api/users/auth/roles/remove/", {"role": "guest"}, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)
        roles = resp.json().get("roles") or []
        self.assertFalse(any(str(r).endswith("guest") or str(r) == "guest" for r in roles), roles)

    def test_logout_returns_200(self):
        # Без авторизации тоже должен вернуть 200 и очистить куки
        resp = self.client.post("/api/users/auth/logout/", {}, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)
