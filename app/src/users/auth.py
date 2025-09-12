from fastapi import HTTPException, status
from sqlalchemy import select
from app.database import DB_SESSION
from app.users.models import User


async def get_current_user(telegram_id: int, db_session: DB_SESSION) -> User:
    query = select(User).filter(User.telegram_id == telegram_id)
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Have no this user"
        )
    return user
