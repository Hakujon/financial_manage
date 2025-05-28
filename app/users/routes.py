from fastapi import APIRouter, Depends

from app.database import DB_SESSION
from app.users.models import User
from app.users.schemas import UserIn
from app.users.dao import UserDAO


router = APIRouter(prefix="/auth",
                   tags=["Работа с авторизацией"])


@router.post("/login")
async def login_user(user_data: UserIn, db_session: DB_SESSION):
    user = UserDAO.fing_one_or_none(user_data.telegram_id, db_session)
    return user
