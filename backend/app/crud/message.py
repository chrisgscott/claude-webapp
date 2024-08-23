from sqlalchemy.orm import Session
from .. import models, schemas

def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def get_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).offset(skip).limit(limit).all()

def update_message(db: Session, message_id: int, message: schemas.MessageCreate):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        for key, value in message.dict().items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message