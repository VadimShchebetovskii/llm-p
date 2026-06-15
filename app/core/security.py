import time
from typing import Any, Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings


ACCESS_TOKEN_EXPIRE_SECONDS = settings.access_token_expire_minutes * 60

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль"""

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет пароль на соответствие хешу"""

    return pwd_context.verify(password, hashed_password)


def _now() -> int:
    """Текущая временная метка в секундах"""

    return int(time.time())


def create_access_token(data: dict[str, Any]) -> str:
    """Создаёт JWT токен доступа"""

    to_encode = data.copy()
    to_encode.update({
        "type": "access",
        "iat": _now(),
        "exp": _now() + ACCESS_TOKEN_EXPIRE_SECONDS,
    })
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Декодирует JWT токен, возвращает None при ошибке"""

    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except JWTError:
        return None
