from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.reviews'
    verbose_name = 'Reviews'

    def ready(self) -> None:
        # Регистрация сигналов пересчёта рейтинга
        # Импорт внутри ready(), чтобы избежать побочных эффектов при миграциях
        from .infrastructure.orm import signals  # noqa: F401

