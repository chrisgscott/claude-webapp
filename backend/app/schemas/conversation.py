from pydantic import BaseModel
from datetime import datetime
from typing import List

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    project_id: int

class Conversation(ConversationBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationWithMessages(Conversation):
    messages: List['Message']

    class Config:
        from_attributes = True