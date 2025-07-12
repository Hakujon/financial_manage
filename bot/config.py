from typing import Optional, ClassVar
from pydantic_settings import SettingsConfigDict, BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    BOT_TOKEN: Optional[str] = None

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        extra="ignore"
    )


settings = Settings()
