# Базовые ошибки/исключения проекта
class DomainError(Exception):
    """Базовая доменная ошибка."""

class ApplicationError(Exception):
    """Ошибка слоя application."""

class InfrastructureError(Exception):
    """Ошибка инфраструктурного слоя."""
