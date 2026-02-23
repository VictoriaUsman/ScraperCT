from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./ct_records.db"

    # App
    APP_NAME: str = "CT Public Records Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:80", "http://localhost"]

    # Scraper
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_MAX_RETRIES: int = 3
    PLAYWRIGHT_HEADLESS: bool = True

    # Scheduler
    SCHEDULER_TIMEZONE: str = "America/New_York"

    # Export
    EXPORT_CHUNK_SIZE: int = 1000


@lru_cache
def get_settings() -> Settings:
    return Settings()
