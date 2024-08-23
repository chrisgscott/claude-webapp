import asyncio
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import engine, get_db
from app.auth import get_current_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import List
from datetime import timedelta
from app.crud import conversation as crud_conversation
from app.schemas import conversation as schemas_conversation

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Add any startup tasks here if needed
    pass

@app.get("/")
async def root():
    return {"message": "Welcome to the Claude-like Web Application API"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=schemas.UserCreate(username=user.username, password=hashed_password))

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    return crud.create_project(db=db, project=project, user_id=current_user.id)

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    projects = crud.get_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

@app.get("/projects/{project_id}", response_model=schemas.ProjectWithDetails)
def read_project(project_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return db_project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")
    return crud.update_project(db=db, project_id=project_id, project=project)

@app.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    return crud.delete_project(db=db, project_id=project_id)

@app.post("/projects/{project_id}/conversations/", response_model=schemas_conversation.Conversation)
def create_conversation(
    project_id: int,
    conversation: schemas_conversation.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    conversation.project_id = project_id
    return crud_conversation.create_conversation(db=db, conversation=conversation)

@app.get("/projects/{project_id}/conversations/", response_model=List[schemas_conversation.Conversation])
def read_conversations(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return crud_conversation.get_conversations(db, project_id=project_id, skip=skip, limit=limit)

@app.get("/conversations/{conversation_id}", response_model=schemas_conversation.ConversationWithMessages)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_conversation = crud_conversation.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db_project = crud.get_project(db, project_id=db_conversation.project_id)
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    return db_conversation

@app.put("/conversations/{conversation_id}", response_model=schemas_conversation.Conversation)
def update_conversation(
    conversation_id: int,
    conversation: schemas_conversation.ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_conversation = crud_conversation.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db_project = crud.get_project(db, project_id=db_conversation.project_id)
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this conversation")
    return crud_conversation.update_conversation(db=db, conversation_id=conversation_id, conversation=conversation)

@app.delete("/conversations/{conversation_id}", response_model=schemas_conversation.Conversation)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_conversation = crud_conversation.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db_project = crud.get_project(db, project_id=db_conversation.project_id)
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this conversation")
    return crud_conversation.delete_conversation(db=db, conversation_id=conversation_id)

@app.post("/conversations/{conversation_id}/messages/", response_model=schemas_conversation.Message)
async def create_message(
    conversation_id: int,
    message: schemas_conversation.MessageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_conversation = crud_conversation.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db_project = crud.get_project(db, project_id=db_conversation.project_id)
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    return await crud_conversation.create_message(db=db, message=message, conversation_id=conversation_id)

@app.get("/conversations/{conversation_id}/messages/", response_model=List[schemas_conversation.Message])
def read_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_conversation = crud_conversation.get_conversation(db, conversation_id=conversation_id)
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db_project = crud.get_project(db, project_id=db_conversation.project_id)
    if db_project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    return crud_conversation.get_messages(db, conversation_id=conversation_id, skip=skip, limit=limit)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}