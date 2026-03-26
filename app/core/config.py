from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./fast_agent_chat.db"
    OPENAI_API_KEY: str = "placeholder_openai_api_key"
    SECRET_KEY: str = "placeholder_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    PROJECT_NAME: str = "FastAgentChat"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
