import os
from pydantic_settings import BaseSettings


_DB_DEFAULT = "postgresql+asyncpg://postgres:postgres@localhost:5432/flashclone"
_REDIS_DEFAULT = "redis://localhost:6379/0"


class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URL", _DB_DEFAULT)
    redis_url: str = os.environ.get("REDIS_URL", _REDIS_DEFAULT)
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    reddit_client_id: str = os.environ.get("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.environ.get("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.environ.get("REDDIT_USER_AGENT", "flashclone/1.0")
    youtube_api_key: str = os.environ.get("YOUTUBE_API_KEY", "")
    celery_broker_url: str = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    cors_origins: str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False, "extra": "ignore"}

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        return url


settings = Settings()

