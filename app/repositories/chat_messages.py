from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ChatMessageOrm


class ChatMessageRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_message(self, role: str, content: str, user_id: int) -> ChatMessageOrm:
        """Сохраняет новое сообщение (пользователя или ассистента)"""

        message = ChatMessageOrm(
            role=role,
            content=content,
            user_id=user_id
        )
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

    async def get_last_n_messages(self, user_id: int, n: int) -> list[ChatMessageOrm]:
        """Возвращает последние N сообщений пользователя (от старых к новым)"""

        result = await self._session.execute(
            select(ChatMessageOrm)
            .where(ChatMessageOrm.user_id == user_id)
            .order_by(ChatMessageOrm.created_at.asc())
            .limit(n)
        )
        return result.scalars().all()

    async def delete_user_history(self, user_id: int) -> None:
        """Удаляет всю историю сообщений пользователя"""

        await self._session.execute(
            delete(ChatMessageOrm).where(ChatMessageOrm.user_id == user_id)
        )
        await self._session.commit()
