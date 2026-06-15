from typing import Any, Dict, Optional


class AppError(Exception):
    """
    Базовое исключение приложения.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConflictError(AppError):
    """
    Исключение конфликта.
    
    Возникает когда пытаются создать объект с уже существующим уникальным полем.
    """
    pass


class UnauthorizedError(AppError):
    """
    Исключение неавторизованного доступа.
    
    Возникает когда пользователь не прошел аутентификацию
    или предоставил неверные учетные данные.
    """
    pass


class ForbiddenError(AppError):
    """
    Исключение запрета доступа.
    
    Возникает когда аутентифицированный пользователь не имеет прав для выполнения операции.
    """
    pass


class NotFoundError(AppError):
    """
    Исключение отсутствия объекта.
    
    Возникает когда запрашиваемый объект не найден в базе данных.
    """
    pass


class ExternalServiceError(AppError):
    """
    Исключение ошибки внешнего сервиса.
    
    Возникает когда внешний сервис вернул ошибку или недоступен.
    """
    pass


class ValidationError(AppError):
    """
    Исключение ошибки валидации.
    
    Возникает когда входные данные не проходят бизнес-валидацию.
    """
    pass


class BadRequestError(AppError):
    """
    Исключение некорректного запроса.
    
    Возникает когда запрос сформирован неправильно (не хватает полей, неправильный формат и т.д.),
    но это не ошибка валидации бизнес-логики.
    """
    pass


class RateLimitError(AppError):
    """
    Исключение превышения лимита запросов.
    
    Возникает когда пользователь превысил допустимое количество запросов.
    """
    pass