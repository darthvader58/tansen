"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    environment: str = "development"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_title: str = "Music Transcription API"
    api_version: str = "1.0.0"
    
    # Firebase Configuration
    firebase_credentials_path: str = "./firebase-credentials.json"
    firebase_project_id: str
    firebase_storage_bucket: str
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7
    
    # Rate Limiting
    rate_limit_transcriptions_per_day: int = 10
    rate_limit_max_concurrent_jobs: int = 2
    
    # External APIs
    youtube_api_key: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    
    # Audio Processing
    max_audio_file_size_mb: int = 50
    supported_audio_formats: str = "mp3,wav,m4a,ogg,flac"
    
    # Storage
    temp_upload_dir: str = "./temp_uploads"
    processed_files_dir: str = "./processed_files"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def supported_formats_list(self) -> List[str]:
        """Get list of supported audio formats."""
        return [fmt.strip() for fmt in self.supported_audio_formats.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_audio_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.temp_upload_dir, exist_ok=True)
os.makedirs(settings.processed_files_dir, exist_ok=True)
