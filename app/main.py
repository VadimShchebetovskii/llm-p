from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import routes_auth, routes_chat
from app.db.base import Base
from app.core.config import settings
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""

    # Запуск: создание таблиц БД
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Остановка: закрытие соединений
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="FastAPI service with JWT auth, SQLite, and OpenRouter LLM proxy",
        version="0.1.0",
        lifespan=lifespan
    )
    
    app.include_router(routes_auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(routes_chat.router, prefix="/chat", tags=["Chat"])
    
    return app


app = create_app()


@app.get("/health")
async def health_check():
    """Проверка состояния сервера"""
    
    return {"status": "ok", "environment": settings.env}
