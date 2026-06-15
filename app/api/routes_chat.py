from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user_id, get_chat_usecase
from app.usecases.chat import ChatUsecase
from app.core.errors import ExternalServiceError
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessagePublic


router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUsecase = Depends(get_chat_usecase)
):
    try:
        response = await chat_usecase.ask(
            user_id=user_id,
            prompt=request.prompt,
            system_instruction=request.system,
            history_limit=request.max_history,
            temperature=request.temperature
        )
        return ChatResponse(answer=response)
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message)


@router.get("/history", response_model=list[ChatMessagePublic])
async def get_chat_history(
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUsecase = Depends(get_chat_usecase)
):
    return await chat_usecase.get_history(user_id, limit)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUsecase = Depends(get_chat_usecase)
):
    await chat_usecase.clear_history(user_id)
