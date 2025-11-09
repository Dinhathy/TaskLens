"""
Configuration management using environment variables.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # OpenAI API Configuration (switched from NVIDIA for reliability)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    vision_model: str = "gpt-4o"  # GPT-4 Omni with vision
    text_model: str = "gpt-4o-mini"  # Cheaper for text-only tasks

    def model_post_init(self, __context):
        """Sanitize API keys and URLs to remove any trailing whitespace/newlines."""
        self.openai_base_url = self.openai_base_url.strip()
        self.openai_api_key = self.openai_api_key.strip()

    # API Configuration
    api_timeout: int = 60
    max_retries: int = 3

    # CORS Configuration
    # Specific origins for local development and production
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://192.168.1.96:8000",  # Local network for mobile testing
        "https://tasklens.netlify.app",  # Production frontend
        "https://tasklensutd.netlify.app"  # Production frontend alternate
    ]

    # App Configuration
    app_name: str = "TaskLens Aggregator Backend"
    app_version: str = "1.0.0"
    debug_mode: bool = True  # Enabled for debugging


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
