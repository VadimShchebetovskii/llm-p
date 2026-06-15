from typing import Optional
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient
from app.schemas.chat import ChatMessagePublic


class ChatUsecase:
    """Бизнес-логика чата: формирование контекста, сохранение истории, вызов LLM"""
    
    def __init__(self, chat_repository: ChatMessageRepository, llm_client: OpenRouterClient):
        self._chat_repo = chat_repository
        self._llm_client = llm_client
    
    
    async def ask(
        self, 
        user_id: int, 
        prompt: str, 
        temperature: float, 
        history_limit: int,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Отправка сообщения в LLM.
        Формирует контекст (системная инструкция + история + текущий запрос),
        сохраняет сообщения в БД, возвращает ответ модели.
        """

        messages = []

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        history_messages = await self._chat_repo.get_last_n_messages(user_id=user_id, n=history_limit)
        
        for msg in history_messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": prompt})
        
        await self._chat_repo.add_message(role="user", content=prompt, user_id=user_id)
        
        response_text = await self._llm_client.chat_completion(messages=messages, temperature=temperature)

        await self._chat_repo.add_message(role="assistant", content=response_text, user_id=user_id)
        
        return response_text


    async def get_history(self, user_id: int, limit: int) -> list[ChatMessagePublic]:
        """Возвращает историю диалога пользователя"""

        messages = await self._chat_repo.get_last_n_messages(user_id, limit)
        return [ChatMessagePublic.model_validate(msg) for msg in messages]
    

    async def clear_history(self, user_id: int) -> None:
        """Очищает всю историю диалога пользователя"""

        await self._chat_repo.delete_user_history(user_id)
