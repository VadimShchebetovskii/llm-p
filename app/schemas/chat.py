from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    prompt: str
    system: Optional[str] = Field(None, description="Системная инструкция (необязательно)")
    max_history: int = Field(default=10, ge=1, le=50, description="Количество сообщений из истории (1-50)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0,
                               description="Креативность модели (0.0 - детерминированно, 2.0 - максимально креативно)")


class ChatResponse(BaseModel):
    answer: str


class ChatMessagePublic(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
