import pytest
from sqlalchemy.orm import Session
from app.crud import conversation as crud_conversation
from app.schemas import conversation as schemas_conversation
from app.models import Conversation, Message
from unittest.mock import patch, MagicMock

@pytest.fixture
def db_session(mocker):
    return mocker.Mock(spec=Session)

@pytest.mark.asyncio
async def test_create_message_user(db_session):
    message = schemas_conversation.MessageCreate(content="Hello, Claude!", role="user")
    conversation_id = 1

    # Mock the database query
    mock_query = MagicMock()
    db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = []  # Simulate an empty conversation history

    with patch("app.services.claude_api.ClaudeAPI.generate_response") as mock_generate_response:
        mock_generate_response.return_value = "Hello! How can I assist you today?"
        
        result = await crud_conversation.create_message(db_session, message, conversation_id)
        
        assert result.content == "Hello, Claude!"
        assert result.role == "user"
        db_session.add.assert_called()
        db_session.commit.assert_called()
        mock_generate_response.assert_called_once()
        
        # Check if AI response was created
        ai_message_call = db_session.add.call_args_list[1][0][0]
        assert isinstance(ai_message_call, Message)
        assert ai_message_call.content == "Hello! How can I assist you today?"
        assert ai_message_call.role == "assistant"

@pytest.mark.asyncio
async def test_create_message_assistant(db_session):
    message = schemas_conversation.MessageCreate(content="This is an assistant message", role="assistant")
    conversation_id = 1

    # Mock the database query
    mock_query = MagicMock()
    db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = []  # Simulate an empty conversation history

    result = await crud_conversation.create_message(db_session, message, conversation_id)
    
    assert result.content == "This is an assistant message"
    assert result.role == "assistant"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_get_conversation_history(db_session):
    conversation_id = 1
    mock_messages = [
        Message(id=1, content="Hello", role="user", conversation_id=conversation_id),
        Message(id=2, content="Hi there!", role="assistant", conversation_id=conversation_id)
    ]
    db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_messages
    
    result = crud_conversation.get_conversation_history(db_session, conversation_id)
    
    assert len(result) == 2
    assert result[0] == {"role": "user", "content": "Hello"}
    assert result[1] == {"role": "assistant", "content": "Hi there!"}