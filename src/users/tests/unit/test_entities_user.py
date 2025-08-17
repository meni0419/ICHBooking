from __future__ import annotations

from django.test import SimpleTestCase

from src.users.domain.entities import UserEntity, UserRole
from src.users.domain.value_objects import Email


class UserEntityTests(SimpleTestCase):
    def test_roles_add_remove_and_has(self):
        u = UserEntity(id=None, name="John", email=Email("john@example.com"))
        self.assertFalse(u.has_role(UserRole.HOST))
        u.add_role(UserRole.HOST)
        self.assertTrue(u.has_role(UserRole.HOST))
        u.add_role(UserRole.GUEST)
        self.assertTrue(u.has_role(UserRole.GUEST))
        u.remove_role(UserRole.HOST)
        self.assertFalse(u.has_role(UserRole.HOST))
