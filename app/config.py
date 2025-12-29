"""Configuration settings for the Court Service"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import sys


from dotenv import load_dotenv
load_dotenv()

API_VERSION = os.getenv("API_VERSION", "v1")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
ENV = os.getenv("ENV", "dev")

# Validate required environment variables
def validate_env_vars():
    """Validate that all required environment variables are set"""
    required_vars = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_ROLE_KEY,
        "SUPABASE_ANON_KEY": SUPABASE_ANON_KEY,
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        print(f"❌ ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)

validate_env_vars()



class Settings(BaseSettings):
    """Application settings"""
    
    # Supabase configuration
    supabase_url: str = SUPABASE_URL
    supabase_key: str = SUPABASE_SERVICE_ROLE_KEY
    
    # API configuration
    api_title: str = "Court Service API"
    api_description: str = "Court Service handling court facility data and location-based queries."     
    
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
