<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, status
=======
from fastapi import APIRouter, Depends, HTTPException, status
>>>>>>> 7b26a2fbb1f3cb3082f0e25bac535595c5a6c35a

from app.database import DB_SESSION
from app.users.schemas import UserIn, FamilyIn, FamilyResponse
from app.users.dao import UserDAO, FamilyDAO


router = APIRouter(prefix="/auth",
                   tags=["Работа с авторизацией"])


@router.post("/login")
async def login_user(user_data: UserIn, db_session: DB_SESSION):
    user = await UserDAO.fing_one_or_none(user_data.telegram_id, db_session)
    if not user:
<<<<<<< HEAD
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user


@router.post("family")
async def create_family(family_data: FamilyIn, db_session: DB_SESSION):
    family = await FamilyDAO.find_one_or_none(family_data.name, db_session)
    if family:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="This family is already created")
    family_db = await FamilyDAO.add(db_session, **family_data.model_dump())
    return {"message": "Family was created",
            "family": FamilyResponse.model_validate(family_db)}
=======
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
>>>>>>> 7b26a2fbb1f3cb3082f0e25bac535595c5a6c35a
