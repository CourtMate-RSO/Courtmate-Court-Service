"""Configuration settings for the Court Service"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


from dotenv import load_dotenv
load_dotenv()

API_VERSION = os.getenv("API_VERSION")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ENV = os.getenv("ENV", "dev")



class Settings(BaseSettings):
    """Application settings"""
    
    # Supabase configuration
    supabase_url: str = SUPABASE_URL
    supabase_key: str = SUPABASE_SERVICE_ROLE_KEY
    
    # API configuration
    api_title: str = "Court Service API"
    api_description: str = "Court Service handeling court facility data and location-based queries."     
    
    api_version: str = API_VERSION
    
    env: str = ENV
    # CORS settings
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:3000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
