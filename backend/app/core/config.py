# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # Security settings
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Claude API settings
    CLAUDE_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20240620"
    CLAUDE_API_VERSION: str = "2023-06-01"
    CLAUDE_MAX_TOKENS: int = 1000

    model_config = ConfigDict(env_file=".env")

settings = Settings()