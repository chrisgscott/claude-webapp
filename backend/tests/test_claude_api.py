import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from app.services.claude_api import ClaudeAPI
from app.core.config import settings
from fastapi import HTTPException

@pytest.fixture
def claude_api():
    return ClaudeAPI()

@pytest.mark.asyncio
async def test_generate_response_success(claude_api):
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from Claude."
                }
            }
        ]
    }
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        response = await claude_api.generate_response([{"role": "user", "content": "Hello, Claude!"}])
        
        assert response == "This is a test response from Claude."
        mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_generate_response_api_error(claude_api):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=500)
        
        with pytest.raises(HTTPException) as exc_info:
            await claude_api.generate_response([{"role": "user", "content": "Hello, Claude!"}])
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Claude API error"