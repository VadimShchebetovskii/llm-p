from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.repositories.users import UserRepository
from app.repositories.chat_messages import ChatMessageRepository
from app.usecases.auth import AuthUsecase
from app.usecases.chat import ChatUsecase
from app.services.openrouter_client import OpenRouterClient
from app.core.config import settings
from app.core.errors import NotFoundError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_session() -> AsyncSession:
    async for session in get_async_session():
        yield session


async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(session)


async def get_chat_message_repository(session: AsyncSession = Depends(get_db_session)) -> ChatMessageRepository:
    return ChatMessageRepository(session)


async def get_auth_usecase(user_repo: UserRepository = Depends(get_user_repository)) -> AuthUsecase:
    return AuthUsecase(user_repo)


async def get_chat_usecase(chat_repo: ChatMessageRepository = Depends(get_chat_message_repository)) -> ChatUsecase:
    llm_client = OpenRouterClient()
    return ChatUsecase(chat_repo, llm_client)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALG]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise credentials_exception
            
        return user_id_int
        
    except JWTError:
        raise credentials_exception


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_usecase: AuthUsecase = Depends(get_auth_usecase)
):
    try:
        user = await auth_usecase.get_profile(user_id)
        return user
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
