from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.repositories.chat_messages import ChatMessageRepository
from app.usecases.auth import AuthUsecase
from app.usecases.chat import ChatUsecase
from app.services.openrouter_client import OpenRouterClient
from app.core.security import decode_access_token
from app.core.errors import NotFoundError
from app.schemas.user import UserPublic


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
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
    
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    try:
        return int(user_id)
    except ValueError:
        raise credentials_exception


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_usecase: AuthUsecase = Depends(get_auth_usecase)
) -> UserPublic:
    try:
        user = await auth_usecase.get_profile(user_id)
        return user
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
