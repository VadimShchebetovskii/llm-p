from app.repositories.users import UserRepository
from app.core.security import create_access_token, hash_password, verify_password
from app.core.errors import ConflictError, UnauthorizedError, NotFoundError
from app.schemas.user import UserPublic


class AuthUsecase:
    """Бизнес-логика аутентификации и управления пользователями"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def register(self, email: str, password: str) -> UserPublic:
        """Регистрация нового пользователя"""

        existing_user = await self._user_repository.get_by_email(email)
        if existing_user:
            raise ConflictError(
                message="User with this email already exists",
                details={"email": email}
            )

        user = await self._user_repository.create(
            email=email,
            password_hash=hash_password(password),
            role="user"
        )
        
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> str:
        """Аутентификация пользователя, возвращает JWT-токен"""

        user = await self._user_repository.get_by_email(email)
        
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError(
                message="Invalid email or password",
                details={"email": email}
            )
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return access_token

    async def get_profile(self, user_id: int) -> UserPublic:
        """Получение профиля пользователя по ID"""

        user = await self._user_repository.get_by_id(user_id)
        
        if not user:
            raise NotFoundError(
                message="User not found",
                details={"user_id": user_id}
            )
        
        return UserPublic.model_validate(user)
