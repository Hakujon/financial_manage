from fastapi import (
    APIRouter, Depends,
    HTTPException, status
    )
from typing import Annotated

from app.finances.service import (
    CategoryService,
    PlanService,
    ExpenseService
)
from app.finances.schemas import (
    ResponseExpense, CreateExpense, FilterExpense,
    BaseCategory, CreatePlan, ResponseCategory, ResponsePlan
)
from app.database import DB_SESSION
from app.finances.caching import get_cache, CacheClient
from app.exceptions.exceptions import (
    DatabaseException, CacheExcpeption,
    ServiceException, NotFoundException
)


router = APIRouter(prefix="/finance", tags=[
    "Work with Expenses, Categories and Plans"])


@router.get("/expenses")
async def get_expenses_by_filter_with_cache(
    request_body: Annotated[FilterExpense, Depends()],
    db_session: DB_SESSION,
    cache: CacheClient = Depends(get_cache)
) -> list[ResponseExpense] | dict:
    try:
        expenses = await ExpenseService.get_expenses_with_cache(
            db_session=db_session,
            expense_filter=request_body,
            cache=cache
        )
        if not expenses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="expenses wasn't found"
            )
        return [ResponseExpense.model_validate(expense)
                for expense in expenses]
    except (DatabaseException, CacheExcpeption) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/expenses")
async def create_expense(
    expense: CreateExpense,
    db_session: DB_SESSION
) -> ResponseExpense:
    try:
        new_expense = await ExpenseService.create_expense(
            db_session=db_session,
            expense=expense
        )

        return ResponseExpense.model_validate(new_expense)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    db_session: DB_SESSION
) -> dict[str, str]:
    try:
        result_of_delete = await ExpenseService.delete_expense(
            db_session=db_session,
            expense_id=expense_id
        )
        if result_of_delete:
            return {"message":
                    "expense was deleted"}
        else:
            raise ServiceException(
                "Expense wasn't deleted"
            )
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/plans")
async def create_new_plan(
    plan: CreatePlan,
    db_session: DB_SESSION
) -> ResponsePlan:
    try:
        new_plan = await PlanService.create_plan(
            db_session=db_session,
            plan=plan
        )
        return ResponsePlan.model_validate(new_plan)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/plans")
async def find_plan(
    category: BaseCategory,
    db_session: DB_SESSION
) -> ResponsePlan:
    try:
        plan_from_db = await PlanService.get_plan(
            db_session=db_session,
            category=category
        )
        if not plan_from_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return ResponsePlan.model_validate(plan_from_db)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: int,
    db_session: DB_SESSION,
    plan: CreatePlan
) -> ResponsePlan:
    try:
        updated_plan = await PlanService.update_plan(
            db_session=db_session,
            plan_id=plan_id,
            plan=plan
        )
        if updated_plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        return ResponsePlan.model_validate(updated_plan)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    db_session: DB_SESSION
) -> dict[str, str]:
    try:
        result_of_delete = await PlanService.delete_plan(
            db_session=db_session,
            plan_id=plan_id
        )
        if result_of_delete:
            return {"message":
                    "plan was deleted"}
        else:
            raise ServiceException(
                "Plan wasn't deleted"
            )
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/categories")
async def get_all_categories(
    db_session: DB_SESSION
) -> list[ResponseCategory]:
    try:
        categories = await CategoryService.get_all_categories(
            db_session=db_session
        )
        return [ResponseCategory.model_validate(category)
                for category in categories]
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/categories")
async def create_category(
    category: BaseCategory,
    db_session: DB_SESSION
) -> ResponseCategory:
    try:
        new_category = await CategoryService.create_category(
            db_session=db_session,
            category=category
        )
        return ResponseCategory.model_validate(new_category)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db_session: DB_SESSION
) -> dict[str, str]:
    try:
        result_of_delete = await CategoryService.delete_category(
            db_session=db_session,
            category_id=category_id
        )
        if result_of_delete:
            return {"message":
                    "category was deleted"}
        else:
            raise ServiceException(
                "Category wasn't deleted"
            )
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
