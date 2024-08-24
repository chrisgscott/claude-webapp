from app.utils.logger import api_logger
from app.core.config import settings
from app.utils.rate_limiter import RateLimiter
import httpx
from fastapi import HTTPException
from unittest.mock import patch, MagicMock

class ClaudeAPIException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Claude API error: {detail}")

class ClaudeAPI:
    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": settings.CLAUDE_API_VERSION
        }
        self.rate_limiter = RateLimiter(max_calls=50, time_frame=60)  # 50 calls per minute

    async def generate_response(self, conversation_history):
        await self.rate_limiter.acquire()

        url = f"{self.base_url}/messages"
        payload = {
            "model": settings.CLAUDE_MODEL,
            "messages": conversation_history,
            "max_tokens": settings.CLAUDE_MAX_TOKENS,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            api_logger.error(f"HTTP error occurred: {exc}")
            raise ClaudeAPIException(exc.response.status_code, str(exc))
        except httpx.RequestError as exc:
            api_logger.error(f"An error occurred while requesting {exc.request.url!r}.")
            raise ClaudeAPIException(500, "Failed to connect to Claude API")

        try:
            response_json = response.json()
            return response_json['content'][0]['text']
        except (KeyError, IndexError) as exc:
            api_logger.error(f"Unexpected response structure: {response.text}")
            raise ClaudeAPIException(500, "Unexpected response from Claude API")