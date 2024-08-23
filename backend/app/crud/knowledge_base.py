from sqlalchemy.orm import Session
from .. import models, schemas

def create_knowledge_base(db: Session, knowledge_base: schemas.KnowledgeBaseCreate):
    db_knowledge_base = models.KnowledgeBase(**knowledge_base.dict())
    db.add(db_knowledge_base)
    db.commit()
    db.refresh(db_knowledge_base)
    return db_knowledge_base

def get_knowledge_base(db: Session, knowledge_base_id: int):
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == knowledge_base_id).first()

def get_knowledge_bases(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.project_id == project_id).offset(skip).limit(limit).all()

def update_knowledge_base(db: Session, knowledge_base_id: int, knowledge_base: schemas.KnowledgeBaseCreate):
    db_knowledge_base = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == knowledge_base_id).first()
    if db_knowledge_base:
        for key, value in knowledge_base.dict().items():
            setattr(db_knowledge_base, key, value)
        db.commit()
        db.refresh(db_knowledge_base)
    return db_knowledge_base

def delete_knowledge_base(db: Session, knowledge_base_id: int):
    db_knowledge_base = db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == knowledge_base_id).first()
    if db_knowledge_base:
        db.delete(db_knowledge_base)
        db.commit()
    return db_knowledge_base