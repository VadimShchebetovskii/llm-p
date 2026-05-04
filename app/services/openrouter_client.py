import httpx
from typing import List, Dict, Any
from app.core.errors import ExternalServiceError
from app.core import config

DEFAULT_TIMEOUT = 30.0
DEFAULT_TEMPERATURE = 0.7

class OpenRouterClient:

    def __init__(self):
        self.base_url = config.OPENROUTER_BASE_URL
        self.api_key = config.OPENROUTER_API_KEY
        self.referer = config.OPENROUTER_SITE_URL
        self.title = config.OPENROUTER_APP_NAME
        
    async def chat_completion(self, model: str, messages: List[Dict[str, str]], temperature: float = DEFAULT_TEMPERATURE) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": self.referer,
                    "X-Title": self.title,
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                },
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code != 200:
                raise ExternalServiceError(f"OpenRouter error: {response.status_code} - {response.text}")
                
            return response.json()
