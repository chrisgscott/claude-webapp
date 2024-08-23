from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)