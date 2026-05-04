from typing import Optional
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUsecase:

    def __init__(
        self, 
        chat_repository: ChatMessageRepository, 
        llm_client: OpenRouterClient,
        system_instruction: Optional[str] = None
    ):
        self._chat_repo = chat_repository
        self._llm_client = llm_client
        self._system_instruction = system_instruction or "You are a helpful assistant."
    
    async def ask(
        self, 
        user_id: int, 
        prompt: str, 
        model: Optional[str] = None,
        history_limit: int = 20,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        messages = []
        
        effective_system = system_instruction if system_instruction is not None else self._system_instruction

        if effective_system:
            messages.append({
                "role": "system",
                "content": effective_system
            })

        history_messages = await self._chat_repo.get_last_n_messages(
            user_id=user_id, 
            n=history_limit
        )

        for msg in history_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        await self._chat_repo.add_message(
            role="user",
            content=prompt,
            user_id=user_id
        )

        response_data = await self._llm_client.chat_completion(
            model=model if model else self._llm_client.default_model,
            messages=messages,
            temperature=temperature
        )
        
        assistant_response = response_data['choices'][0]['message']['content']

        await self._chat_repo.add_message(
            role="assistant",
            content=assistant_response,
            user_id=user_id
        )

        return assistant_response
    

    async def get_history(self, user_id: int, limit: int = 50) -> list:
        return await self._chat_repo.get_last_n_messages(user_id, limit)
    

    async def clear_history(self, user_id: int) -> None:
        await self._chat_repo.delete_user_history(user_id)
