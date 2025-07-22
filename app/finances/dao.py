from app.dao.base import BaseDAO
from app.finances.models import Expense
from app.finances.schemas import FilterExpense
from app.finances.caching import CacheClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, distinct

from typing import Callable, Any


class ExpenseDAO(BaseDAO):
    model = Expense

    @staticmethod
    def build_conditions(filters_dict: dict):
        filter_map: dict[str, Callable[[Any], Any]] = {
            "start_amount": lambda x: Expense.amount >= x,
            "head_amount": lambda x: Expense.amount <= x,
            "category": lambda x: Expense.category == x,
            "start_date": lambda x: Expense.created_at >= x,
            "end_date": lambda x: Expense.created_at <= x
                }
        return [
            filter_map[key](value) for key, value in filters_dict.items()
            if key in filter_map
            ]

    @classmethod
    async def find_id_by_filter(cls, db_session: AsyncSession,
                                filters: FilterExpense):
        conditions = cls.build_conditions(
            filters.model_dump(exclude_none=True)
        )
        query = (select(cls.model.id).where(and_(*conditions))
                 if conditions else select(cls.model.id))
        result = await db_session.execute(query)
        return result.scalars().all()

    @classmethod
    async def find_by_id(cls, db_session: AsyncSession,
                         ids: list[int]):
        if not ids:
            return []
        query = select(cls.model).where(cls.model.id.in_(ids))
        result = await db_session.execute(query)
        return result.scalars().all()



    @classmethod
    async def find_categories(cls, db_session: AsyncSession):
        query = select(distinct(Expense.category))
        result = await db_session.execute(query)
        categories = result.scalars().all()
        return categories
