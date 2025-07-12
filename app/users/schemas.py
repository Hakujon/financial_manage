from pydantic import BaseModel


class UserIn(BaseModel):
    telegram_id: int
    username: str


class FamilyIn(BaseModel):
    name: str


class FamilyResponse(FamilyIn):
    id: int
