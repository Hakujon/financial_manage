from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.exceptions.exceptions import (
    DatabaseException, CacheExcpeption,
    NotFoundException
    )
from app.finances.dao import (
    ExpenseDao, PlanDao, CategoryDao
)
from app.finances.models import (
    Category, Expense, Plan
)
from app.finances.schemas import (
    BaseCategory, CreateExpense, FilterExpense,
    CreatePlan
)
from app.finances.caching import CacheClient


class CategoryService():
    @classmethod
    async def create_category(
        cls,
        db_session: AsyncSession,
        category: BaseCategory
    ) -> Category:
        try:
            async with db_session.begin():
                new_category = await CategoryDao.add(
                    db_session=db_session,
                    **category.model_dump()
                )
            return new_category
        except IntegrityError as e:
            await db_session.rollback()
            raise DatabaseException(
                f"Database exc: {e}"
            ) from e
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(
                f"Database exc: {e}"
            ) from e

    @classmethod
    async def get_all_categories(
        cls,
        db_session: AsyncSession
    ) -> List[Category]:
        try:
            async with db_session.begin():
                categories = await CategoryDao.find_all(
                    db_session=db_session
                )
            if not categories:
                raise NotFoundException("Categories not found")
            return categories
        except SQLAlchemyError as e:
            raise DatabaseException(
                f"Database exc: {e}"
            ) from e

    @classmethod
    async def delete_category(
        cls,
        db_session: AsyncSession,
        category_id: int
    ) -> bool:
        try:
            async with db_session.begin():
                result_of_delete = await CategoryDao.delete_instance(
                    db_session=db_session,
                    data_id=category_id
                )
            return result_of_delete
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"database exc: {e}") from e


class PlanService():
    @classmethod
    async def create_plan(
        cls,
        db_session: AsyncSession,
        plan: CreatePlan
    ) -> Plan:
        try:
            async with db_session.begin():
                new_plan = await PlanDao.add_plan(
                    db_session=db_session,
                    category=plan.category,
                    start_date=plan.start_date,
                    planned_amount=plan.planned_amount
                )
            return new_plan
        except IntegrityError as e:
            await db_session.rollback()
            raise DatabaseException(f"database exc: {e}") from e
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"database exc: {e}") from e

    @classmethod
    async def get_plan(
        cls,
        db_session: AsyncSession,
        category: BaseCategory
    ) -> Optional[Plan]:
        try:
            async with db_session.begin():
                plan = await PlanDao.find_one_or_none_plan(
                    db_session=db_session,
                    category=category
                )
            return plan
        except SQLAlchemyError as e:
            raise DatabaseException(
                f"Database exc: {e}"
            ) from e

    @classmethod
    async def delete_plan(
        cls,
        db_session: AsyncSession,
        plan_id: int
    ) -> bool:
        try:
            async with db_session.begin():
                plan_to_delete = await PlanDao.find_one_or_none(
                    db_session=db_session,
                    id=plan_id
                )

                if not plan_to_delete:
                    raise NotFoundException("Plan not found")
                plan_to_delete_id = plan_to_delete.id
                result_of_delete = await PlanDao.delete_instance(
                    db_session=db_session,
                    data_id=plan_to_delete_id
                )
            return result_of_delete
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"database exc: {e}") from e

    @classmethod
    async def update_plan(
        cls,
        db_session: AsyncSession,
        plan_id: int,
        plan: CreatePlan
    ) -> Optional[Plan]:
        try:
            updated_plan = await PlanDao.update_instance(
                db_session=db_session,
                data_id=plan_id,
                **plan.model_dump()
            )
            return updated_plan
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"database exc: {e}") from e


class ExpenseService():
    @classmethod
    async def create_expense(
        cls,
        db_session: AsyncSession,
        expense: CreateExpense,
        retries: int = 5
    ) -> Expense:
        for attempt in range(retries):
            try:
                async with db_session.begin():
                    await PlanDao.find_or_create_plan(
                        db_session=db_session,
                        category=BaseCategory(
                            **expense.category.model_dump()
                        )
                    )
                    db_category = await CategoryDao.find_one_or_none(
                        db_session=db_session,
                        name=expense.category.name
                    )
                    if db_category is None:
                        raise DatabaseException("Can't find category")

                    expense_dict = expense.model_dump()
                    expense_dict["category_id"] = db_category.id
                    del expense_dict["category"]

                    new_expense = await ExpenseDao.add(
                        db_session=db_session,
                        **expense_dict
                    )
                    return new_expense
            except IntegrityError as e:
                if (
                    "unique constraint" in str(e).lower()
                    ) and (
                        attempt < retries - 1
                        ):
                    await db_session.rollback()
                    continue
                else:
                    await db_session.rollback()
                    raise DatabaseException(
                        f"database exc: {e}"
                    ) from e
            except SQLAlchemyError as e:
                await db_session.rollback()
                raise DatabaseException(
                     f"Database error: {e}"
                ) from e
        raise DatabaseException(
            "Failed to create expense"
        )

    @classmethod
    async def get_expenses_with_cache(
        cls,
        db_session: AsyncSession,
        expense_filter: FilterExpense,
        cache: CacheClient
    ) -> Optional[List[Expense]]:
        try:
            expenses_ids = await ExpenseDao.find_id_expense_by_filter(
                db_session=db_session,
                expense_filter=expense_filter
            )
            if not expenses_ids:
                return []
            cached_expenses = await cache.get_many_expenses(
                ids=expenses_ids
            )
            cached_ids = {expense.id for expense in cached_expenses}
            not_cached_ids = list(set(expenses_ids)-cached_ids)
            if not_cached_ids:
                expenses_from_db = await ExpenseDao.find_expenses_by_id(
                    db_session=db_session,
                    ids=not_cached_ids
                )
                await cache.set_many_expenses(expenses=expenses_from_db)
            expenses = cached_expenses + expenses_from_db
            ordered_expenses = sorted(expenses, key=lambda x: x.category_id)
            return ordered_expenses
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"Database exc: {e}") from e
        except CacheExcpeption as e:
            raise e

    @classmethod
    async def delete_expense(
        cls,
        db_session: AsyncSession,
        expense_id: int
    ) -> bool:
        try:
            async with db_session.begin():
                result_of_delete = await ExpenseDao.delete_instance(
                    db_session=db_session,
                    data_id=expense_id
                )
            return result_of_delete
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"database exc: {e}") from e
