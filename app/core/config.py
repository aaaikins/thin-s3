"""Configuration management using Pydantic BaseSettings"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS configuration
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"
    s3_bucket: str = "test-bucket"
    s3_endpoint_url: str = "http://localstack:4566"
    
    # Redis configuration
    redis_url: str = "redis://redis:6379"
    
    # FastAPI configuration
    debug: bool = False
    api_title: str = "Thin S3 API"
    api_version: str = "0.1.0"
    
    # TTL configuration
    default_ttl_seconds: int = 3600
    
    #Load .env file
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra='allow')


# Create settings instance
settings = Settings()
