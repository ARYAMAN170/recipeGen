# stir-backend/app/core/config.py
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional
import os

# Robustly find .env file
# This looks for .env in the current directory, or one level up
env_path = ".env"
if not os.path.exists(env_path):
    potential_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(potential_path):
        env_path = potential_path

load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # MongoDB settings
    MONGO_URI: str
    GEMINI_API_KEY: str
    FIREWORKS_API_KEY: str
    OPENROUTER_API_KEY: str
    CLOUD_NAME: str
    CLOUD_API_KEY: str
    CLOUD_API_SECRET: str

    # JWT settings (optional for now)
    JWT_SECRET_KEY: Optional[str] = "your-secret-key-here"
    JWT_ALGORITHM: Optional[str] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = "../.env"
        extra = "allow"  # Allow extra fields from .env

settings = Settings()