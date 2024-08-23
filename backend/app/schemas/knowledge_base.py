from pydantic import BaseModel
from datetime import datetime

class KnowledgeBaseBase(BaseModel):
    title: str
    content: str

class KnowledgeBaseCreate(KnowledgeBaseBase):
    project_id: int

class KnowledgeBase(KnowledgeBaseBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True