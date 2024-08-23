from sqlalchemy.orm import Session
from .. import models, schemas

def create_conversation(db: Session, conversation: schemas.ConversationCreate):
    db_conversation = models.Conversation(**conversation.dict())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()

def get_conversations(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Conversation).filter(models.Conversation.project_id == project_id).offset(skip).limit(limit).all()

def update_conversation(db: Session, conversation_id: int, conversation: schemas.ConversationCreate):
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conversation:
        for key, value in conversation.dict().items():
            setattr(db_conversation, key, value)
        db.commit()
        db.refresh(db_conversation)
    return db_conversation

def delete_conversation(db: Session, conversation_id: int):
    db_conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
    return db_conversation