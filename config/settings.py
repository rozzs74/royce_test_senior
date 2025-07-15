import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings configuration"""
    
    # API Key for application access
    APP_API_KEY = "hBGZPVk5MPNX7hrU3Ut2akE4"
    API_KEY = APP_API_KEY  # For compatibility
    
    @classmethod
    def admin_web_api_key(cls):
        """Get the admin web API key"""
        return cls.APP_API_KEY
    
    @classmethod
    def get_api_key(cls):
        """Get the application API key"""
        return cls.APP_API_KEY
    
    # Individual Database Configuration
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "bowling_rental")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))

    # Application settings
    APP_NAME = "Bowling Shoes Rental Service"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "A FastAPI service for managing bowling shoe rentals with LLM-powered discount calculations"