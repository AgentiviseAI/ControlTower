"""
Core configuration and settings module
"""
import os
import logging
from typing import Any, Dict, Optional, List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


def load_environment():
    """Load environment based on ENVIRONMENT variable"""
    # Check for environment from multiple sources
    env = os.getenv("ENVIRONMENT")
    
    # If no environment is set or set to something other than 'prod', default to 'dev'
    if env != "prod":
        env = "dev"
    
    if env == "prod":
        env_file = ".env.prod"
    else:
        env_file = ".env.dev"
    
    # Load the environment file if it exists
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"Loaded environment from {env_file}")
    else:
        print(f"Environment file {env_file} not found, using defaults")


# Load environment before creating settings
load_environment()


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    app_name: str = "AI Platform Backend"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="dev", env="ENVIRONMENT")
    
    # Server settings
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Database settings
    database_type: str = Field(default="sqlite", env="DATABASE_TYPE")
    database_url: str = Field(default="sqlite:///./ai_platform.db", env="DATABASE_URL")
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="ai_platform", env="POSTGRES_DB")
    
    # Security settings
    secret_key: str = Field(default="dev-secret-key-not-for-production", env="SECRET_KEY")
    jwt_secret_key: str = Field(default="dev-jwt-secret-key-not-for-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS settings
    cors_origins: Union[str, List[str]] = Field(default="http://localhost:3000,http://localhost:5173", env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: Union[str, List[str]] = Field(default="*", env="CORS_METHODS")
    cors_headers: Union[str, List[str]] = Field(default="*", env="CORS_HEADERS")
    
    # Auth Service Configuration
    auth_service_url: str = Field(default="http://localhost:8000", env="AUTH_SERVICE_URL")
    
    # External services
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    azure_openai_endpoint: str = Field(default="", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="", env="AZURE_OPENAI_API_KEY")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    log_format: str = Field(default="detailed", env="LOG_FORMAT")
    
    # Monitoring settings
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS", alias="metrics_enabled")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # API settings
    api_v1_prefix: str = "/api/v1"

    @field_validator('cors_origins')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('cors_methods')
    @classmethod
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(',')]
        return v
    
    @field_validator('cors_headers')
    @classmethod
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(',')]
        return v
    
    model_config = {"env_file": ".env", "case_sensitive": False}


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get the appropriate database URL based on configuration"""
    # If DATABASE_URL is explicitly set and it's PostgreSQL, use it directly
    if settings.database_url and settings.database_url.startswith("postgresql"):
        return settings.database_url
    elif settings.database_type.lower() == "postgresql":
        return (
            f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )
    else:
        return settings.database_url


def get_log_config() -> Dict[str, Any]:
    """Get logging configuration"""
    # Determine format based on log_format setting
    if settings.log_format == "detailed":
        default_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    elif settings.log_format == "json":
        default_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        default_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": default_format,
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": "detailed",
                "filename": settings.log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console", "file"],
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }
