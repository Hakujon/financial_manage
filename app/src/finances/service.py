from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.exceptions.exceptions import (
    DatabaseException, CacheExcpeption,
    NotFoundException
    )
from src.finances.dao import (
    ExpenseDao, PlanDao, CategoryDao
)
from src.finances.models import (
    Category, Expense, Plan
)
from src.finances.schemas import (
    BaseCategory, CreateExpense, FilterExpense,
    CreatePlan
)
from src.finances.caching import CacheClient


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
            await db_session.flush()
            await db_session.refresh(new_plan)
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
    ) -> Plan:
        try:
            async with db_session.begin():
                plan = await PlanDao.find_one_or_none_plan(
                    db_session=db_session,
                    category=category
                )
                if not plan:
                    raise NotFoundException("Not found plan")
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

    @classmethod
    async def calculate_remaining_of_plan(
        cls,
        db_session: AsyncSession,
        category: BaseCategory,
        cache: CacheClient
    ) -> float:
        try:
            async with db_session.begin():
                plan = await cls.get_plan(
                    db_session=db_session,
                    category=category)

                end_date = plan.end_date
                start_date = plan.start_date
                expense_filter = FilterExpense(
                    start_amount=None,
                    head_amount=None,
                    category=category.category_name,
                    start_date=start_date,
                    end_date=end_date
                )
                expenses = await ExpenseService.get_expenses_with_cache(
                    db_session=db_session,
                    expense_filter=expense_filter,
                    cache=cache
                )

                expenses_amount = ExpenseService.calculate_sum_of_expenses(
                    expenses)

                remaining = plan.planned_amount - expenses_amount
                return remaining

        except NotFoundException as e:
            await db_session.rollback()
            raise e
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise DatabaseException(f"Database exc: {e}") from e


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
                    # db_category = await CategoryDao.find_or_create_category(
                    #     db_session=db_session,
                    #     category=expense.category
                    # )

                    await PlanDao.find_or_create_plan(
                        db_session=db_session,
                        category=BaseCategory(
                            **expense.category.model_dump()
                        )
                    )
                    db_category = await CategoryDao.find_one_or_none(
                        db_session=db_session,
                        category_name=expense.category.category_name
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
                    await db_session.refresh(new_expense)
                    new_expense.category = db_category
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

    @staticmethod
    def calculate_sum_of_expenses(
        expenses: Optional[List[Expense]]
    ) -> float:
        if not expenses:
            return 0
        return sum(expense.amount for expense in expenses)
