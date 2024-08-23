from pydantic import BaseModel
from datetime import datetime
from typing import List

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectWithDetails(Project):
    conversations: List['Conversation']
    knowledge_base: List['KnowledgeBase']

    class Config:
        from_attributes = True