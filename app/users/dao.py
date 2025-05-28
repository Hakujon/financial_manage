from app.users.models import User
from app.dao.base import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def fing_one_or_none(
        cls, telegram_id: int, db_session: AsyncSession
            ):
        query = select(User).filter(User.telegram_id == telegram_id)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()
