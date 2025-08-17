from __future__ import annotations

from django.test import SimpleTestCase

from src.shared.errors import ApplicationError
from src.users.application.commands import AddRoleCommand, RemoveRoleCommand
from src.users.application.use_cases.assign_roles import AddRoleUseCase, RemoveRoleUseCase
from src.users.domain.entities import UserEntity, UserRole
from src.users.domain.repository_interfaces import IUserRepository
from src.users.domain.value_objects import Email


class FakeUserRepoRoles(IUserRepository):
    def __init__(self):
        self._by_id = {}
        self._id = 1

    def get_by_id(self, user_id: int):
        return self._by_id.get(user_id)

    def get_by_email(self, email: Email):
        for u in self._by_id.values():
            if str(u.email) == str(email):
                return u
        return None

    def exists_by_email(self, email: Email) -> bool:
        return self.get_by_email(email) is not None

    def list_by_ids(self, ids):
        return [self._by_id[i] for i in ids if i in self._by_id]

    def create(self, user: UserEntity) -> UserEntity:
        self._id += 1
        user.id = self._id
        self._by_id[user.id] = user
        return user

    def update(self, user: UserEntity) -> UserEntity:
        self._by_id[user.id] = user
        return user


class AssignRolesUseCasesTests(SimpleTestCase):
    def setUp(self):
        self.repo = FakeUserRepoRoles()
        self.user = UserEntity(id=10, name="Roley", email=Email("role@example.com"))
        self.repo._by_id[self.user.id] = self.user

    def test_add_role_host(self):
        uc = AddRoleUseCase(users=self.repo)
        dto = uc.execute(AddRoleCommand(user_id=self.user.id, role=UserRole.HOST))
        self.assertIn(UserRole.HOST, dto.roles)

    def test_remove_role_guest(self):
        # добавим гостя, затем снимем
        self.user.roles.add(UserRole.GUEST)
        uc = RemoveRoleUseCase(users=self.repo)
        dto = uc.execute(RemoveRoleCommand(user_id=self.user.id, role=UserRole.GUEST))
        self.assertNotIn(UserRole.GUEST, dto.roles)

    def test_add_role_user_not_found(self):
        uc = AddRoleUseCase(users=self.repo)
        with self.assertRaises(ApplicationError):
            uc.execute(AddRoleCommand(user_id=999, role=UserRole.HOST))

    def test_remove_role_user_not_found(self):
        uc = RemoveRoleUseCase(users=self.repo)
        with self.assertRaises(ApplicationError):
            uc.execute(RemoveRoleCommand(user_id=999, role=UserRole.GUEST))
