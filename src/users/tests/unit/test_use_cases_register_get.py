from __future__ import annotations

from typing import Optional, Iterable, Dict, List

from django.test import SimpleTestCase

from src.shared.errors import ApplicationError
from src.users.application.commands import RegisterUserCommand
from src.users.application.queries import GetCurrentUserQuery
from src.users.application.use_cases.register_user import RegisterUserUseCase
from src.users.application.use_cases.get_current_user import GetCurrentUserUseCase
from src.users.application.ports import IAuthProvider
from src.users.domain.entities import UserEntity, UserRole
from src.users.domain.repository_interfaces import IUserRepository
from src.users.domain.value_objects import Email


class FakeUserRepo(IUserRepository):
    def __init__(self):
        self._by_id: Dict[int, UserEntity] = {}
        self._id_seq = 100

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        return self._by_id.get(user_id)

    def get_by_email(self, email: Email) -> Optional[UserEntity]:
        for u in self._by_id.values():
            if str(u.email) == str(email):
                return u
        return None

    def exists_by_email(self, email: Email) -> bool:
        return self.get_by_email(email) is not None

    def list_by_ids(self, ids: Iterable[int]) -> List[UserEntity]:
        return [self._by_id[i] for i in ids if i in self._by_id]

    def create(self, user: UserEntity) -> UserEntity:
        self._id_seq += 1
        user.id = self._id_seq
        self._by_id[user.id] = user
        return user

    def update(self, user: UserEntity) -> UserEntity:
        assert user.id is not None
        self._by_id[user.id] = user
        return user


class FakeAuthProvider(IAuthProvider):
    def __init__(self, users: FakeUserRepo):
        self._users = users

    def create_user_with_password(self, user: UserEntity, password: str) -> UserEntity:
        # Имитируем установку пароля и сохранение через инфраструктуру
        return self._users.create(user)


class RegisterAndGetUserUseCasesTests(SimpleTestCase):
    def setUp(self):
        self.users = FakeUserRepo()
        self.auth = FakeAuthProvider(self.users)

    def test_register_guest_by_default_and_get_current(self):
        uc = RegisterUserUseCase(users=self.users, auth=self.auth)
        dto = uc.execute(
            RegisterUserCommand(
                name="John",
                email=Email("john@example.com"),
                password="secret1",
                password_confirm="secret1",
                initial_roles=None,
            )
        )
        self.assertGreater(dto.id, 0)
        self.assertEqual(dto.name, "John")
        self.assertEqual(dto.email, "john@example.com")
        # По умолчанию роль guest
        self.assertIn(UserRole.GUEST, dto.roles)

        # get_current_user
        gc = GetCurrentUserUseCase(users=self.users)
        dto2 = gc.execute(GetCurrentUserQuery(user_id=dto.id))
        self.assertEqual(dto2.id, dto.id)
        self.assertEqual(dto2.email, dto.email)

    def test_register_with_mismatched_passwords(self):
        uc = RegisterUserUseCase(users=self.users, auth=self.auth)
        with self.assertRaises(ApplicationError):
            uc.execute(
                RegisterUserCommand(
                    name="Jane",
                    email=Email("jane@example.com"),
                    password="a",
                    password_confirm="b",
                    initial_roles=None,
                )
            )

    def test_register_with_existing_email(self):
        # заранее создадим пользователя с этим email
        existing = UserEntity(id=None, name="X", email=Email("dup@example.com"))
        self.users.create(existing)

        uc = RegisterUserUseCase(users=self.users, auth=self.auth)
        with self.assertRaises(ApplicationError):
            uc.execute(
                RegisterUserCommand(
                    name="Jane",
                    email=Email("dup@example.com"),
                    password="pwd",
                    password_confirm="pwd",
                    initial_roles=None,
                )
            )

    def test_register_with_initial_roles_host(self):
        uc = RegisterUserUseCase(users=self.users, auth=self.auth)
        dto = uc.execute(
            RegisterUserCommand(
                name="Hosty",
                email=Email("host@example.com"),
                password="pwd",
                password_confirm="pwd",
                initial_roles=[UserRole.HOST],
            )
        )
        self.assertIn(UserRole.HOST, dto.roles)
        self.assertNotIn(UserRole.GUEST, dto.roles)
