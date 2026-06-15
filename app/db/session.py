from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings


engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.sqlite_path}",
    echo=settings.env == "local"  # Логи SQL в режиме разработки
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)