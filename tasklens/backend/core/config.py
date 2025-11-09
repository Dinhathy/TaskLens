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

    # NVIDIA API Configuration
    nvidia_api_key: str = ""
    nano2_vlm_url: str = "https://ai.api.nvidia.com/v1/vlm/nvidia/nemotron-nano-2-vlm"
    nano3_llm_url: str = "https://ai.api.nvidia.com/v1/chat/completions"

    # API Configuration
    api_timeout: int = 60
    max_retries: int = 3

    # CORS Configuration
    # Allow all origins for demo/hackathon - restrict in production!
    cors_origins: list = ["*"]

    # App Configuration
    app_name: str = "TaskLens Aggregator Backend"
    app_version: str = "1.0.0"
    debug_mode: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
