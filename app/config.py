from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str

<<<<<<< HEAD
    BOT_TOKEN: str

=======
>>>>>>> 7b26a2fbb1f3cb3082f0e25bac535595c5a6c35a
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        extra="ignore"
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}/{self.DB_NAME}")


<<<<<<< HEAD
settings = Settings()  # type: ignore
=======
settings = Settings() # type: ignore
>>>>>>> 7b26a2fbb1f3cb3082f0e25bac535595c5a6c35a
