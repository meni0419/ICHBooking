# Архитектура (набросок)


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
