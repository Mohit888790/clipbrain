"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase
    supabase_url: str
    supabase_service_key: str
    
    # Redis
    redis_url: str
    
    # AI Services
    deepgram_api_key: str
    gemini_api_key: str
    
    # Application
    allowed_platforms: str = "youtube,instagram,tiktok,facebook"
    max_video_duration_seconds: int = 7200
    signed_url_ttl_seconds: int = 900
    
    # Rate Limiting
    ingest_rate_limit_per_hour: int = 10
    search_rate_limit_per_hour: int = 100
    
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def allowed_platforms_list(self) -> list[str]:
        """Get allowed platforms as a list."""
        return [p.strip() for p in self.allowed_platforms.split(",")]


# Global settings instance
settings = Settings()
