from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
<<<<<<< HEAD


class FamilyIn(BaseModel):
    name: str


class FamilyResponse(FamilyIn):
    id: int
=======
    telegram_id: int
>>>>>>> 7b26a2fbb1f3cb3082f0e25bac535595c5a6c35a
