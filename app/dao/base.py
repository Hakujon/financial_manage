from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc.import SQLAlchemyError


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, session:AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
           await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        await session.refresh(new_instance)
        return (new_instance)

    @classmethod
    async def delete(cls, session: AsyncSession, data_id: int):
        query = delete(cls.model).filter_by(id=data_id)
        await session.execute(query)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return {"message":
                "data was deleted"}
