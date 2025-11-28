from functools import lru_cache
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///newsfeed.db"
    CHROMADB_PATH: str = "./chroma_data"
    FETCH_INTERVAL_MINUTES: int = 15
    LOG_LEVEL: str = "INFO"

    GEMINI_API_KEY: Optional[SecretStr] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
