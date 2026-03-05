"""
Configuration settings for the Fasty application.

This module handles loading and validating configuration from environment variables
and configuration files.
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
import os
from pydantic import BaseSettings, Field, validator
from pydantic.types import DirectoryPath, FilePath
from pydantic.env_settings import SettingsSourceCallable


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    APP_NAME: str = "Fasty API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File paths
    BASE_DIR: DirectoryPath = Path(__file__).parent.parent.parent
    CONFIG_FILE: FilePath = BASE_DIR / "fasty.yml"
    CERTS_DIR: DirectoryPath = BASE_DIR / "certs"

    # API settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Fasty"
    VERSION: str = "0.1.0"

    # Rate limiting
    RATE_LIMIT: str = "100/minute"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings."""
    return settings
