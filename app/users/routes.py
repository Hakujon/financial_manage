from fastapi import APIRouter, Depends, HTTPException, status

from app.database import DB_SESSION
from app.users.models import User
from app.users.schemas import UserIn
from app.users.dao import UserDAO


router = APIRouter(prefix="/auth",
                   tags=["Работа с авторизацией"])


@router.post("/login")
async def login_user(user_data: UserIn, db_session: DB_SESSION):
    user = await UserDAO.fing_one_or_none(user_data.telegram_id, db_session)
    if not user:
        user = await UserDAO.add(db_session, **user_data.model_dump())
    return {"status": "ok"}


@router.delete("/login")
async def logout_user(user_data: UserIn, db_session: DB_SESSION):
    user = await UserDAO.fing_one_or_none(user_data.telegram_id, db_session)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="You are not user")
    await UserDAO.delete(db_session, user.id)
    return {"message":
            "user was deleted"}
