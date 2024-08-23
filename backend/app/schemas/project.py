from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None

class Project(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectWithDetails(Project):
    conversations: List['Conversation'] = []
    knowledge_base: List['KnowledgeBase'] = []

    model_config = ConfigDict(from_attributes=True)

from .conversation import Conversation
from .knowledge_base import KnowledgeBase