# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # Security settings
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Claude API settings
    CLAUDE_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()