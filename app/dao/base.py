from typing import (
    Type, TypeVar, Generic,
    List, Optional
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseDAO(Generic[T]):
    model: Type[T] = None

    @classmethod
    async def find_all(
        cls,
        db_session: AsyncSession,
        **filter_by
    ) -> List[T]:
        query = select(cls.model).filter_by(**filter_by)
        result = await db_session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def find_one_or_none(
        cls,
        db_session: AsyncSession,
        **filter_by
    ) -> Optional[T]:
        query = select(cls.model).filter_by(**filter_by)
        result = await db_session.execute(query)
        return result.scalars().one_or_none()

    @classmethod
    async def add(
        cls,
        db_session: AsyncSession,
        **values
    ) -> T:
        new_instance = cls.model(**values)
        db_session.add(new_instance)
        return new_instance

    @classmethod
    async def update_instance(
        cls,
        db_session: AsyncSession,
        data_id: int,
        **values
    ) -> Optional[T]:
        instance = await cls.find_one_or_none(
            db_session=db_session,
            id=data_id
        )
        if not instance:
            return None
        for field, value in values.items():
            setattr(instance, field, value)
        # db_session.add(instance=instance)
        return instance

    @classmethod
    async def delete_instance(
        cls,
        db_session: AsyncSession,
        data_id: int
    ) -> bool:
        instance = cls.find_one_or_none(
            db_session=db_session,
            id=data_id
        )
        if not instance:
            return False
        await db_session.delete(instance=instance)
        return True
