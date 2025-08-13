# ICHBooking — План проекта (ROADMAP)

Цели:
- Реализовать функционал по требованиям (обязательные, дополнительные).
- Следовать чистой архитектуре: domain / application / infrastructure / interfaces.
- Использовать DRF, JWT (в куках), MySQL; позже — Docker и деплой на AWS.

Статусные теги:
- [ ] Не начато
- [~] В процессе
- [x] Готово

Навигация:
- Этап 0. Инфраструктура и зависимости
- Этап 1. Пользователи, аутентификация и авторизация (обязательно)
- Этап 2. Объявления (CRUD + доступность) (обязательно)
- Этап 3. Поиск, фильтрация, сортировка (обязательно)
- Этап 4. Бронирования (обязательно)
- Этап 5. Рейтинги и отзывы (обязательно)
- Этап 6. Дополнительные требования (популярность, история поиска, просмотры)
- Этап 7. Тесты (опционально, но рекомендуется)
- Этап 8. Docker и AWS (дополнительно)
- Приложение: Git-flow и порядок задач

---

## Этап 0. Инфраструктура и зависимости

Задача: Подготовить окружение, пакеты, настройки.

- [x] Переключение на MySQL
  - Настройки: core/settings.py (DATABASES)
  - Установить драйвер: mysqlclient (или PyMySQL)
  - Создать базу данных ICHBooking в MySQL, настроить доступы в ENV.
  - Миграции: python manage.py makemigrations && migrate

- [x] Подключение DRF
  - Установить djangorestframework
  - core/settings.py: добавить 'rest_framework' и базовые REST_FRAMEWORK настройки

- [x] JWT в куках (DRF + SimpleJWT)
  - Установить djangorestframework-simplejwt
  - core/settings.py: SIMPLE_JWT конфиг (lifetime, cookie names, rotation, samesite, secure), DRF аутентификатор
  - src/users/interfaces/rest/urls.py: JWT endpoints (login/refresh/logout)
  - src/users/interfaces/rest/views.py: вью для логина/логаута с установкой/очисткой cookie
  - CSRF: продумать стратегию (например, чтение CSRF из куки + заголовок)

- [x] Swagger/OpenAPI
  - Установить drf-spectacular (или drf-yasg)
  - core/settings.py: spectacular настройки
  - core/urls.py: схемы /api/schema/, /api/docs/

- [x] Базовая конфигурация INSTALLED_APPS
  - core/settings.py: 'src.users', 'src.accommodations', 'src.bookings', 'src.reviews', 'src.common' (payments отложим)

Файлы и что в них будет:
- core/settings.py — конфигурация БД (MySQL), DRF, JWT, Swagger.
- core/urls.py — включение роутов приложений и Swagger.
- src/*/interfaces/rest/urls.py — маршруты по приложениям.

---

## Этап 1. Пользователи, аутентификация и авторизация (обязательное)

Цели: Регистрация, вход, роли (арендодатель/арендатор), разграничение прав.

- [x] Доменные модели и роли
  - src/users/domain/entities.py — UserEntity (id, name, email, roles: {host, guest}, is_active)
  - src/users/domain/value_objects.py — Email, PasswordHash (при необходимости)
  - src/users/domain/repository_interfaces.py — IUserRepository (контракты поиска/создания)
  - src/users/domain/services.py — правила назначений ролей

- [x] Приложение (use-cases)
  - src/users/application/commands.py — RegisterUser, AssignRoles
  - src/users/application/queries.py — GetCurrentUser
  - src/users/application/use_cases/ — обработчики команд/запросов

- [ ] Инфраструктура (ORM и репозитории)
  - src/users/infrastructure/orm/models.py — кастомная модель User (на базе AbstractUser)
    - Поля: name (или first_name/last_name), email(unique), роли (например, JSON/ManyToMany/Choices/флаги)
  - src/users/infrastructure/repositories.py — Django-реализация IUserRepository
  - core/settings.py — AUTH_USER_MODEL = 'users.User'
  - src/users/infrastructure/admin.py — регистрация модели в админке

- [ ] Интерфейсы (REST, JWT)
  - src/users/interfaces/rest/serializers.py — RegisterSerializer, UserSerializer
  - src/users/interfaces/rest/views.py — RegisterView, LoginView (JWT cookie), LogoutView, MeView
  - src/users/interfaces/rest/permissions.py — IsHost, IsGuest
  - src/users/interfaces/rest/urls.py — /auth/register/, /auth/login/, /auth/logout/, /auth/me/

- [ ] Права доступа
  - Роль host: создавать/редактировать/удалять свои объявления
  - Роль guest: просматривать/фильтровать

---

## Этап 2. Объявления (CRUD + доступность) (обязательное)

Цели: Создание, редактирование, удаление, доступность (активно/неактивно).

- [ ] Домейн
  - src/accommodations/domain/entities.py — Accommodation (id, title, description, location, price, rooms, type, is_active, owner_id, created_at)
  - src/accommodations/domain/value_objects.py — Location (city, region, country="DE"), Money/Price, HousingType (Enum)
  - src/accommodations/domain/dtos.py — AccommodationDTO
  - src/accommodations/domain/repository_interfaces.py — IAccommodationRepository
  - src/accommodations/domain/services.py — инварианты (валидность цены, названия и т.д.)

- [ ] Приложение (use-cases)
  - src/accommodations/application/commands.py — CreateAccommodation, UpdateAccommodation, DeleteAccommodation, ToggleAvailability
  - src/accommodations/application/queries.py — GetAccommodationById
  - src/accommodations/application/use_cases/ — обработчики

- [ ] Инфраструктура
  - src/accommodations/infrastructure/orm/models.py — ORM модель Accommodation (FK на users.User)
  - src/accommodations/infrastructure/repositories.py — реализация IAccommodationRepository
  - src/accommodations/infrastructure/admin.py — регистрация модели

- [ ] Интерфейсы (REST)
  - src/accommodations/interfaces/rest/serializers.py — AccommodationCreateUpdateSerializer, AccommodationDetailSerializer
  - src/accommodations/interfaces/rest/views.py — ViewSet/классы для CRUD и toggle
    - Create/Update/Delete — только для host-владельца
    - Toggle availability — только владелец
  - src/accommodations/interfaces/rest/filters.py — фильтры позже (этап 3)
  - src/accommodations/interfaces/rest/permissions.py — IsOwnerOrReadOnly, IsHost
  - src/accommodations/interfaces/rest/urls.py — /accommodations/…

---

## Этап 3. Поиск, фильтрация, сортировка (обязательное)

Цели: Поиск по ключевым словам в заголовке/описании, фильтрация и сортировка.

- [ ] Домейн
  - src/accommodations/domain/dtos.py — SearchQueryDTO (keyword, price_min/max, city/region, rooms_min/max, type, sort)
  - src/accommodations/domain/services.py — правила валидации запроса

- [ ] Приложение
  - src/accommodations/application/queries.py — SearchAccommodations
  - src/accommodations/application/use_cases/ — обработчик поиска (делегирует в репозиторий; параметризует сортировку)

- [ ] Инфраструктура
  - src/accommodations/infrastructure/repositories.py — методы фильтрации по ORM (Q, annotate)
  - Индексы в БД: title, city/region, created_at, price

- [ ] Интерфейсы (REST)
  - src/accommodations/interfaces/rest/filters.py — DRF фильтры/FilterSet
  - src/accommodations/interfaces/rest/views.py — endpoint поиска: /accommodations/search/
  - Поддержать сортировку: price asc/desc, created_at asc/desc

---

## Этап 4. Бронирования (обязательное)

Цели: Создание, просмотр своих, отмена, подтверждение/отклонение хостом.

- [ ] Домейн
  - src/bookings/domain/entities.py — Booking (id, accommodation_id, guest_id, host_id, start_date, end_date, status: REQUESTED/CONFIRMED/CANCELLED/REJECTED, created_at)
  - src/bookings/domain/value_objects.py — StayPeriod (валидация дат)
  - src/bookings/domain/dtos.py — BookingDTO
  - src/bookings/domain/repository_interfaces.py — IBookingRepository
  - src/bookings/domain/services.py — валидация пересечений дат, политика отмены

- [ ] Приложение
  - src/bookings/application/commands.py — CreateBooking, CancelBooking, ConfirmBooking, RejectBooking
  - src/bookings/application/queries.py — ListMyBookings (guest), ListMyRequests (host)
  - src/bookings/application/use_cases/ — обработчики

- [ ] Инфраструктура
  - src/bookings/infrastructure/orm/models.py — ORM Booking (FK на User, Accommodation)
  - src/bookings/infrastructure/repositories.py — реализация IBookingRepository; проверки пересечений в запросах

- [ ] Интерфейсы (REST)
  - src/bookings/interfaces/rest/serializers.py — BookingCreateSerializer, BookingDetailSerializer
  - src/bookings/interfaces/rest/views.py — эндпоинты:
    - POST /bookings/ — создать
    - GET /bookings/me/ — мои (guest)
    - GET /bookings/requests/ — запросы, где я host
    - POST /bookings/{id}/cancel/
    - POST /bookings/{id}/confirm/
    - POST /bookings/{id}/reject/
  - Разрешения: гостю — создавать/смотреть свои; хосту — подтверждать/отклонять заявки на свои объявления

---

## Этап 5. Рейтинги и отзывы (обязательное)

Цели: Оставить отзыв к объявлению после завершённого бронирования; список отзывов.

- [ ] Домейн
  - src/reviews/domain/entities.py — Review (id, accommodation_id, author_id, rating, text, created_at)
  - src/reviews/domain/dtos.py — ReviewDTO
  - src/reviews/domain/repository_interfaces.py — IReviewRepository
  - src/reviews/domain/services.py — политика: отзыв можно оставить только гостю, у которого было завершённое бронирование

- [ ] Приложение
  - src/reviews/application/commands.py — CreateReview
  - src/reviews/application/queries.py — ListReviewsForAccommodation
  - src/reviews/application/use_cases/ — обработчики

- [ ] Инфраструктура
  - src/reviews/infrastructure/orm/models.py — ORM Review
  - src/reviews/infrastructure/repositories.py — реализация IReviewRepository

- [ ] Интерфейсы (REST)
  - src/reviews/interfaces/rest/serializers.py — ReviewCreateSerializer, ReviewSerializer
  - src/reviews/interfaces/rest/views.py — POST /reviews/, GET /accommodations/{id}/reviews/
  - Права: автор — только гость с завершённым бронированием данного объявления

---

## Этап 6. Дополнительные требования

### 6.1. Популярность
- [ ] Подсчёт просмотров/отзывов для сортировки
  - Инфраструктура: агрегирующие запросы
  - Интерфейсы: параметр sort=popular

### 6.2. История поиска
- [ ] Логирование поисковых запросов
  - src/common/domain/entities.py — SearchQueryLog
  - src/common/infrastructure/orm/models.py — ORM модель
  - Запись при вызове поиска (этап 3)
  - Эндпоинт: GET /search/popular/ — топ частых ключевых слов

### 6.3. История просмотров
- [ ] Логирование фактов просмотра объявления
  - src/common/domain/entities.py — ListingViewLog
  - src/common/infrastructure/orm/models.py — ORM модель
  - Хук в детальный просмотр объявления
  - Эндпоинт сортировки по просмотрам (этап 3)

---

## Этап 7. Тесты (рекомендуется)

- [ ] Unit-тесты доменных сервисов
  - src/*/tests/unit/ — тесты правил, инвариантов
- [ ] Интеграционные тесты интерфейсов (DRF)
  - src/*/tests/integration/ — API кейсы: аутентификация, CRUD объявлений, поиск, бронирование, отзывы
- [ ] Фикстуры: фабрики доменных DTO

---

## Этап 8. Docker и AWS

- [ ] Docker
  - Dockerfile — сборка Django + gunicorn
  - docker-compose.yml — web + MySQL
  - ENV/секреты — через переменные окружения
- [ ] AWS
  - EC2 для приложения, RDS для MySQL (при наличии)
  - Настройка reverse proxy (Nginx), статика/медиа (S3 — опционально)
  - CI/CD (GitHub Actions) — деплой на EC2

---

## Git-flow и порядок задач

Рекомендуемый порядок веток:
1. feature/setup-infra (Этап 0)
2. feature/users-auth (Этап 1)
3. feature/accommodations-crud (Этап 2)
4. feature/search-filter-sort (Этап 3)
5. feature/bookings (Этап 4)
6. feature/reviews (Этап 5)
7. feature/extra-popularity-search-history-views (Этап 6)
8. feature/tests (Этап 7)
9. feature/docker-aws (Этап 8)

Каждая ветка:
- Реализует соответствующие задачи по слоям (domain → application → infrastructure → interfaces).
- Пишем миграции только на уровне infrastructure/orm/models.py.
- После успешного локального тестирования → PR → ревью → merge в main.

---

## Сводка по файлам (куда писать код)

- Пользователи:
  - domain: src/users/domain/* (entities, repository_interfaces, services)
  - application: src/users/application/* (commands/queries/use_cases)
  - infrastructure: src/users/infrastructure/orm/models.py, repositories.py
  - interfaces: src/users/interfaces/rest/* (serializers, views, urls, permissions)

- Объявления:
  - domain: src/accommodations/domain/*
  - application: src/accommodations/application/*
  - infrastructure: src/accommodations/infrastructure/*
  - interfaces: src/accommodations/interfaces/rest/*

- Поиск/Фильтры/Сортировка:
  - application/queries + infrastructure/repositories + interfaces/rest/filters

- Бронирования:
  - domain/application/infrastructure/interfaces в src/bookings/*

- Отзывы:
  - domain/application/infrastructure/interfaces в src/reviews/*

- Общие сущности:
  - src/common/* (история поиска, просмотров)
  - src/shared/* (errors, result, utils)

---

## Примечания по безопасности и UX

- JWT в куках: HttpOnly, Secure (в проде), SameSite=Lax/None (если нужен кросс-домен), рефреш-токен в куке, access — опционально в куке/памяти.
- CSRF: для cookie-based аутентификации — поддерживать CSRF токен.
- Валидация входных данных: serializers + доменные правила.
- Пагинация и лимиты: использовать DRF пагинацию; ограничивать размер выборок.