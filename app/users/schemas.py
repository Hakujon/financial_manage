from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    telegram_id: int
