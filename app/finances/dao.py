from typing import Optional, Callable, Any
from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.finances.schemas import (
    BaseCategory, FilterExpense
)
from app.dao.base import BaseDAO
from app.finances.models import (
    Expense, Category, Plan
)


class CategoryDao(BaseDAO[Category]):
    model = Category

    @classmethod
    async def find_or_create_category(
        cls,
        db_session: AsyncSession,
        category: BaseCategory,
    ) -> Category:
        db_category = await cls.find_one_or_none(
            db_session=db_session,
            name=category.name
        )
        if db_category is None:
            db_category = await cls.add(
                db_session=db_session,
                **category.model_dump()
            )
        return db_category


class PlanDao(BaseDAO[Plan]):
    model = Plan

    @staticmethod
    def calculate_start_date(first_day_of_plan: int | None = None):
        if first_day_of_plan is None:
            first_day_of_plan = 5
        today = datetime.now()
        if today.day < first_day_of_plan:
            start_date = today - relativedelta(months=1)
        start_date.replace(day=first_day_of_plan)
        return start_date

    @classmethod
    async def add_plan(
        cls,
        db_session: AsyncSession,
        category: BaseCategory,
        start_date: datetime | None = None,
        planned_amount: float | None = None
    ) -> Plan:
        if start_date is None:
            start_date = cls.calculate_start_date()
        end_date: datetime = start_date + relativedelta(months=1)
        end_date = end_date - relativedelta(days=1)
        if planned_amount is None:
            planned_amount = 0
        db_category = await CategoryDao.find_or_create_category(
            db_session=db_session,
            category=category
        )
        new_plan = Plan(
            start_date=start_date,
            end_date=end_date,
            category_id=db_category.id,
            planned_amount=planned_amount
        )
        db_session.add(new_plan)
        return new_plan

    @classmethod
    async def find_one_or_none_plan(
        cls,
        db_session: AsyncSession,
        category: BaseCategory
    ) -> Optional[Plan]:
        today = datetime.now()
        db_category = await CategoryDao.find_one_or_none(
            db_session=db_session,
            name=category.name
        )
        if db_category is None:
            return None
        query = (
                select(cls.model).
                where(cls.model.start_date < today,
                      cls.model.end_date > today,
                      cls.model.category_id == db_category.id)
                )
        result = await db_session.execute(query)
        db_plan = result.scalars().one_or_none()
        return db_plan

    @classmethod
    async def find_or_create_plan(
        cls,
        db_session,
        category: BaseCategory
    ) -> Plan:
        db_plan = await cls.find_one_or_none_plan(
            db_session=db_session,
            category=category
        )
        if db_plan is None:
            start_date = cls.calculate_start_date()
            db_plan = await cls.add_plan(
                db_session=db_session,
                category=category,
                start_date=start_date
            )
        return db_plan


class ExpenseDao(BaseDAO[Expense]):
    model = Expense

    @staticmethod
    def build_conditions(expense_filter: FilterExpense) -> list:
        filter_map: dict[str, Callable[[Any], Any]] = {
            "start_amount": lambda x: Expense.amount >= x,
            "head_amount": lambda x: Expense.amount < x,
            "category": lambda x: Expense.category == x,
            "start_date": lambda x: Expense.created_at >= x,
            "end_date": lambda x: Expense.created_at <= x
        }
        filter_dict = expense_filter.model_dump()
        filter_list = [
            filter_map[key](value) for key, value in filter_dict.items()
            if (
                key in filter_map and
                not (key == "category" and value == "All")
            )
        ]
        return filter_list

    @classmethod
    async def find_id_expense_by_filter(
        cls,
        db_session: AsyncSession,
        expense_filter: FilterExpense
    ) -> list[int]:
        conditions = cls.build_conditions(expense_filter)
        query = select(cls.model.id).where(and_(*conditions))
        result = await db_session.execute(query)
        expense_ids = result.scalars().all()
        return list(expense_ids)

    @classmethod
    async def find_expenses_by_id(
        cls,
        db_session: AsyncSession,
        ids: list[int]
    ) -> list[Expense]:
        if not ids:
            return []
        query = select(cls.model).where(cls.model.id.in_(ids))
        result = await db_session.execute(query)
        expenses = list(result.scalars().all())
        return expenses
