from typing import Optional
from pydantic_settings import SettingsConfigDict, BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    BOT_TOKEN: Optional[str] = None
    URL_API: Optional[str] = None
    REDIS_HOST: Optional[str] = "localhost"
    REDIS_PORT: Optional[int] = 6379

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        extra="ignore"
    )


settings = Settings()
