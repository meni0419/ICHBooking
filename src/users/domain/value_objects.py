# Слой domain: Value Objects (неизменяемые)
from __future__ import annotations

import re
from dataclasses import dataclass


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    """Value Object для email. Хранит валидированное значение."""
    value: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.value):
            raise ValueError("Invalid email format")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PasswordHash:
    """
    Обёртка над хешем пароля.
    Хеширование выполняется во внешнем слое (infrastructure).
    """
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 20:
            # Простейшая эвристика: хеш не должен быть коротким/пустым
            raise ValueError("Invalid password hash")

    def __str__(self) -> str:
        return self.value
