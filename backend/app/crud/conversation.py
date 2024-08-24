from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime
from app.services.claude_api import ClaudeAPI, ClaudeAPIException
from app.utils.logger import db_logger
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

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
    try:
        db_message = models.Message(**message.dict(), conversation_id=conversation_id)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        if message.role == "user":
            try:
                claude_api = ClaudeAPI()
                conversation_history = get_conversation_history(db, conversation_id)
                ai_response = await claude_api.generate_response(conversation_history)
                
                ai_message = models.Message(
                    content=ai_response,
                    role="assistant",
                    conversation_id=conversation_id
                )
                db.add(ai_message)
                db.commit()
                db.refresh(ai_message)
            except ClaudeAPIException as exc:
                db_logger.error(f"Claude API error: {exc}")
                raise HTTPException(status_code=exc.status_code, detail=exc.detail)
            except HTTPException as exc:
                if exc.status_code == 429:
                    db_logger.warning("Rate limit exceeded for Claude API")
                raise

        return db_message
    except SQLAlchemyError as exc:
        db_logger.error(f"Database error: {exc}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

def get_conversation_history(db: Session, conversation_id: int):
    messages = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.asc()).all()
    return [{"role": msg.role, "content": msg.content} for msg in messages] if messages else []

def get_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).offset(skip).limit(limit).all()