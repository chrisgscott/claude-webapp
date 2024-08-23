from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime
from app.services.claude_api import ClaudeAPI

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

def update_conversation(db: Session, conversation_id: int, conversation: schemas.ConversationUpdate):
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        update_data = conversation.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_conversation, key, value)
        db_conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_conversation)
    return db_conversation

def delete_conversation(db: Session, conversation_id: int):
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
    return db_conversation

async def create_message(db: Session, message: schemas.MessageCreate, conversation_id: int):
    db_message = models.Message(**message.model_dump(), conversation_id=conversation_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    conversation_history = get_conversation_history(db, conversation_id)
    
    if message.role == "user":
        claude_api = ClaudeAPI()
        ai_response = await claude_api.generate_response(conversation_history)
        ai_message = models.Message(content=ai_response, role="assistant", conversation_id=conversation_id)
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

    return db_message

def get_conversation_history(db: Session, conversation_id: int):
    messages = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.asc()).all()
    return [{"role": msg.role, "content": msg.content} for msg in messages] if messages else []

def get_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).offset(skip).limit(limit).all()