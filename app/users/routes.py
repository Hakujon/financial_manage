from fastapi import APIRouter, HTTPException, status

from app.database import DB_SESSION
from app.users.schemas import UserIn, FamilyIn, FamilyResponse
from app.users.dao import UserDAO, FamilyDAO


router = APIRouter(prefix="/auth",
                   tags=["Работа с авторизацией"])


@router.post("/login")
async def login_user(user_data: UserIn, db_session: DB_SESSION):
    user = await UserDAO.fing_one_or_none(user_data.telegram_id, db_session)
    if not user:
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
