#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Создает каркас чистой архитектуры для Django-проекта:
- src/ как корневая папка исходников
- Приложения: users, accommodations, bookings, payments, reviews, common
- Слои в каждом приложении: domain, application (use_cases), infrastructure, interfaces (rest), tests
- Минимальные __init__.py и заглушки с TODO

Предполагается, что в корне уже есть:
- manage.py
- core/ (Django project)
- template/ (опционально)
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

APPS = [
    "users",  # Кастомный пользователь, роли: admin, host(арендодатель), guest(арендатор)
    "accommodations",  # Объявления/объекты размещения, адреса, удобства, фото
    "bookings",  # Бронирования, статусы, правила отмены
    "payments",  # Платежи, провайдеры, транзакции (интеграции позже)
    "reviews",  # Отзывы и рейтинги
    "common",  # Общие компоненты, кросс-доменные вещи (например, локации, справочники)
]

LAYER_DIRS = {
    "domain": [
        "entities.py",
        "value_objects.py",
        "dtos.py",
        "repository_interfaces.py",
        "services.py",
        "__init__.py",
    ],
    "application": [
        "commands.py",
        "queries.py",
        "use_cases/__init__.py",
        "__init__.py",
    ],
    "infrastructure": [
        "orm/__init__.py",
        "orm/models.py",
        "repositories.py",
        "migrations/__init__.py",
        "admin.py",
        "__init__.py",
    ],
    "interfaces": [
        "rest/__init__.py",
        "rest/serializers.py",
        "rest/views.py",
        "rest/urls.py",
        "rest/permissions.py",
        "rest/filters.py",
        "__init__.py",
    ],
    "tests": [
        "unit/__init__.py",
        "integration/__init__.py",
        "__init__.py",
    ],
}

COMMON_EXTRA = {
    # Утилиты и общие компоненты
    "shared": [
        "__init__.py",
        "result.py",  # Результаты операций (Ok/Err) — опционально
        "errors.py",  # Базовые исключения
        "typing.py",  # Типы/алиасы
        "utils.py",  # Небизнесовые утилиты
        "pagination.py",  # Общая пагинация
        "validation.py",  # Общая валидация
    ],
}

# Минимальные заглушки для создаваемых файлов
FILE_TEMPLATES = {
    "domain/entities.py": """# Слой domain: сущности предметной области
# TODO: описать Entities (без зависимостей от Django)
""",
    "domain/value_objects.py": """# Слой domain: Value Objects (неизменяемые)
# TODO: описать Value Objects
""",
    "domain/dtos.py": """# Слой domain: DTO для обмена данными между слоями (без зависимостей от Django)
# Рекомендуется использовать dataclasses из стандартной библиотеки
# from dataclasses import dataclass
# @dataclass
# class ExampleDTO: ...
""",
    "domain/repository_interfaces.py": """# Слой domain: контракты репозиториев
# TODO: описать абстрактные интерфейсы репозиториев (protocols/ABC)
""",
    "domain/services.py": """# Слой domain: доменные сервисы (чистые функции/классы без инфраструктуры)
# TODO: оформить доменные инварианты и бизнес-правила
""",
    "application/commands.py": """# Слой application: команды (модифицирующие сценарии)
# TODO: определить команды и обработчики
""",
    "application/queries.py": """# Слой application: запросы (чтение)
# TODO: определить запросы и обработчики
""",
    "infrastructure/orm/models.py": """# Слой infrastructure: Django ORM модели
from django.db import models

# TODO: добавить реальные модели ORM, связанные с domain через маппинг (не переносить доменные сущности)
""",
    "infrastructure/repositories.py": """# Слой infrastructure: реализации репозиториев (Django ORM)
# TODO: адаптеры для domain.repository_interfaces
""",
    "infrastructure/admin.py": """# Django admin регистрации (инфраструктурный слой)
from django.contrib import admin
# TODO: зарегистрировать модели
""",
    "interfaces/rest/serializers.py": """# Слой interfaces: DRF сериалайзеры (если используете DRF)
# TODO: добавить сериалайзеры. При желании можно держать маппинг DTO <-> Serializer
""",
    "interfaces/rest/views.py": """# Слой interfaces: представления/ендпоинты
# TODO: добавить контроллеры/вьюхи. В идеале зависеть от application-слоя
""",
    "interfaces/rest/urls.py": """# Слой interfaces: маршрутизация текущего приложения
from django.urls import path

urlpatterns = [
    # TODO: добавить url-паттерны
]
""",
    "interfaces/rest/permissions.py": """# Слой interfaces: разрешения/доступ
# TODO: описать пермишены
""",
    "interfaces/rest/filters.py": """# Слой interfaces: фильтры
# TODO: описать фильтры
""",
    "tests/__init__.py": """# Пакет тестов
""",
    "tests/unit/__init__.py": """# Юнит-тесты
""",
    "tests/integration/__init__.py": """# Интеграционные тесты
""",
}

USERS_APP_HINT = """\"\"\"Подсказка по users:
- Рекомендуется завести кастомную модель пользователя на базе AbstractUser (или AbstractBaseUser).
- Роли:
    - admin (администратор — через is_staff/is_superuser или отдельную роль)
    - host (арендодатель)
    - guest (арендатор)
  Переключаемую модель ролей проще держать как множество ролей у пользователя (многозначный Enum/флаги),
  а разруливание — через пермишены и policy в application/interfaces слоях.
- Переопределите AUTH_USER_MODEL в core/settings.py на 'users.User' после добавления реализации.
\"\"\""""

ACCOMMODATIONS_HINT = """\"\"\"Подсказка по accommodations:
- Доменные сущности: Accommodation, Address, Amenity, Photo и т.п.
- Инфраструктурная ORM-модель может включать связи с пользователем-хостом.
\"\"\""""

BOOKINGS_HINT = """\"\"\"Подсказка по bookings:
- Доменные сущности: Booking, StayPeriod, CancellationPolicy.
- Сценарии: создание бронирования, отмена, подтверждение.
- Валидация конфликтов дат в domain/application слоях.
\"\"\""""

PAYMENTS_HINT = """\"\"\"Подсказка по payments:
- Доменные сущности: Payment, Transaction, Refund.
- Интеграции с провайдерами — адаптеры в infrastructure.
\"\"\""""

REVIEWS_HINT = """\"\"\"Подсказка по reviews:
- Доменные сущности: Review, Rating.
- Политики кто и когда может оставлять отзывы.
\"\"\""""

COMMON_HINT = """\"\"\"Подсказка по common:
- Общие справочники, локации, общие политики, пайплайны валидации.
\"\"\""""

SHARED_FILES_TEMPLATES = {
    "shared/result.py": """# Общий тип результата (Option/Result-подобные паттерны)
# TODO: при необходимости ввести Result[OK, Err] для явной обработки ошибок
""",
    "shared/errors.py": """# Базовые ошибки/исключения проекта
class DomainError(Exception):
    \"\"\"Базовая доменная ошибка.\"\"\"

class ApplicationError(Exception):
    \"\"\"Ошибка слоя application.\"\"\"

class InfrastructureError(Exception):
    \"\"\"Ошибка инфраструктурного слоя.\"\"\"
""",
    "shared/typing.py": """# Общие типы/алиасы, Protocols при желании
# from typing import Protocol, TypeVar, Generic, Optional, Iterable, Mapping, Sequence
""",
    "shared/utils.py": """# Небизнесовые утилиты
# TODO: логирование, helpers и т.п.
""",
    "shared/pagination.py": """# Общая пагинация и структуры ответа
# TODO: стандартные структуры пагинации
""",
    "shared/validation.py": """# Общая валидация/правила
# TODO: валидаторы вне доменной логики
""",
}

APP_HINTS = {
    "users": USERS_APP_HINT,
    "accommodations": ACCOMMODATIONS_HINT,
    "bookings": BOOKINGS_HINT,
    "payments": PAYMENTS_HINT,
    "reviews": REVIEWS_HINT,
    "common": COMMON_HINT,
}


def write_file(path: Path, content: str) -> None:
    # Гарантируем, что родительские директории существуют
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def touch_init(path: Path) -> None:
    # Гарантируем, что родительские директории существуют
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")


def main() -> int:
    created = []

    SRC.mkdir(exist_ok=True)

    write_file(
        SRC / "README.md",
        "# src\n\nКаркас чистой архитектуры: domain / application / infrastructure / interfaces / tests.\n"
    )

    (SRC / "shared").mkdir(exist_ok=True)
    touch_init(SRC / "shared" / "__init__.py")
    for fname in COMMON_EXTRA["shared"]:
        if fname != "__init__.py":
            write_file(SRC / "shared" / fname, SHARED_FILES_TEMPLATES.get(f"shared/{fname}", ""))

    for app in APPS:
        app_root = SRC / app
        app_root.mkdir(exist_ok=True)
        touch_init(app_root / "__init__.py")

        write_file(
            app_root / "apps.py",
            f"""from django.apps import AppConfig\n\n\nclass {app.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'src.{app}'\n"""
        )

        write_file(
            app_root / "urls.py",
            "from django.urls import include, path\n\nurlpatterns = [\n    path('api/', include('src.%s.interfaces.rest.urls')),\n]\n" % app
        )

        write_file(
            app_root / "README.md",
            f"# {app}\n\n{APP_HINTS.get(app, '').strip()}\n"
        )

        # Создаём слои и файлы: сначала гарантируем директории, затем пишем файлы
        for layer, files in LAYER_DIRS.items():
            layer_root = app_root / layer
            layer_root.mkdir(parents=True, exist_ok=True)
            for f in files:
                fpath = layer_root / f
                # Всегда создаём родительские каталоги
                fpath.parent.mkdir(parents=True, exist_ok=True)
                if fpath.name.endswith(".py"):
                    key = f"{layer}/{f}".replace("\\", "/")
                    content = FILE_TEMPLATES.get(key, "")
                    write_file(fpath, content if content is not None else "")
                else:
                    # На случай непитоновских файлов — создаём пустышки
                    fpath.touch(exist_ok=True)

        created.append(str(app_root.relative_to(ROOT)))

    write_file(
        SRC / "ARCHITECTURE.md",
        """# Архитектура (набросок)


- domain: Чистые сущности, value objects, доменные сервисы, интерфейсы репозиториев, DTO (без зависимостей от Django).
- application: use-cases (commands/queries), оркестрация, транзакционные границы. Зависит от domain.
- infrastructure: реализации интерфейсов (ORM, репозитории, внешние сервисы, admin, миграции). Зависит от application/domain.
- interfaces: контроллеры/вьюхи/сериалайзеры/роуты, адаптация внешних интерфейсов к application-слою.
- tests: unit и integration тесты по слоям.
- shared: общие небизнесовые утилиты/типы/обработчики ошибок.

Подключение приложений в core/settings.py через INSTALLED_APPS:
- 'src.users', 'src.accommodations', 'src.bookings', 'src.payments', 'src.reviews', 'src.common'

Рекомендации:
- Определите кастомную модель пользователя (users.infrastructure.orm.models) и установите AUTH_USER_MODEL = 'users.User'
- Держите маппинг между domain-entities и ORM-моделями в инфраструктуре (mapper функции).
- DTO лучше оставить dataclasses без зависимостей.
"""
    )

    print("Структура создана/обновлена.")
    for p in created:
        print(f" - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
