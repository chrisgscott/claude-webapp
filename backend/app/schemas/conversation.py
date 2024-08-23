# app/schemas/conversation.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    project_id: int

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationWithMessages(Conversation):
    messages: List[Message] = []

    model_config = ConfigDict(from_attributes=True)