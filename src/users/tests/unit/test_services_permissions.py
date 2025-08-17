from __future__ import annotations

from django.test import SimpleTestCase

from src.users.domain.entities import UserEntity, UserRole
from src.users.domain.services import (
    assign_role, revoke_role,
    can_create_accommodation, can_manage_own_accommodations, can_book_accommodation,
)
from src.users.domain.value_objects import Email


class UserServicesPermissionTests(SimpleTestCase):
    def make_user(self, roles=()):
        u = UserEntity(id=1, name="Jane", email=Email("jane@example.com"), is_active=True)
        for r in roles:
            assign_role(u, r)
        return u

    def test_assign_and_revoke(self):
        u = self.make_user()
        assign_role(u, UserRole.HOST)
        self.assertTrue(u.has_role(UserRole.HOST))
        revoke_role(u, UserRole.HOST)
        self.assertFalse(u.has_role(UserRole.HOST))

    def test_permissions_active_user(self):
        u_host = self.make_user([UserRole.HOST])
        self.assertTrue(can_create_accommodation(u_host))
        self.assertTrue(can_manage_own_accommodations(u_host))
        self.assertFalse(can_book_accommodation(u_host))

        u_guest = self.make_user([UserRole.GUEST])
        self.assertFalse(can_create_accommodation(u_guest))
        self.assertFalse(can_manage_own_accommodations(u_guest))
        self.assertTrue(can_book_accommodation(u_guest))

    def test_inactive_user(self):
        u = UserEntity(id=2, name="Inactive", email=Email("inactive@example.com"), is_active=False)
        assign_role(u, UserRole.HOST)
        assign_role(u, UserRole.GUEST)
        self.assertFalse(can_create_accommodation(u))
        self.assertFalse(can_manage_own_accommodations(u))
        self.assertFalse(can_book_accommodation(u))
