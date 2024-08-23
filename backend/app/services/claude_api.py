import httpx
from fastapi import HTTPException
from app.core.config import settings

class ClaudeAPI:
    def __init__(self):
        self.api_key = settings.CLAUDE_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

    async def generate_response(self, conversation_history):
        url = f"{self.base_url}/messages"
        payload = {
            "model": "claude-3-5-sonnet-20240620",
            "messages": conversation_history,
            "max_tokens": 1000,  # Adjust as needed
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Claude API error")

        return response.json()['choices'][0]['message']['content']