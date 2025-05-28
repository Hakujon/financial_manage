from pydantic import BaseModel


class UserIn(BaseModel):
    telegram_id: int
    username: str
