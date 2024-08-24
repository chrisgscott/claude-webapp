import pytest
import httpx
from httpx import AsyncClient, HTTPStatusError
from unittest.mock import patch, MagicMock
from app.services.claude_api import ClaudeAPI, ClaudeAPIException
from app.core.config import settings
from app.utils.logger import api_logger

@pytest.fixture
def claude_api():
    return ClaudeAPI()

@pytest.mark.asyncio
async def test_generate_response_success(claude_api):
    response = await claude_api.generate_response([{"role": "user", "content": "Hello, Claude!"}])
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_generate_response_api_error(claude_api):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError("HTTP Error", request=MagicMock(), response=MagicMock(status_code=401))
        
        with pytest.raises(ClaudeAPIException) as exc_info:
            await claude_api.generate_response([{"role": "user", "content": "Hello, Claude!"}])
    
    assert exc_info.value.status_code == 401
    assert "HTTP Error" in str(exc_info.value)
    api_logger.error(f"Test error log: {exc_info.value}")