from fastapi import APIRouter, Depends
from typing import Annotated
from app.finances.schemas import ResponseExpense, CreateExpense, FilterExpense
from app.finances.dao import ExpenseDAO
from app.database import DB_SESSION


router = APIRouter(prefix="/finance", tags=["Work with Expenses"])


@router.get("/")
async def get_expenses_by_filter(
    request_body: Annotated[FilterExpense, Depends()],
    db_session: DB_SESSION,
) -> list[ResponseExpense] | dict:
    expenses = await ExpenseDAO.find_by_filter(
        db_session, request_body)
    if not expenses:
        return {"message":
                "Expenses not found"}
    return [ResponseExpense.model_validate(expense) for expense in expenses]


@router.get("/all")
async def get_all_expenses(
    db_session: DB_SESSION
) -> list[ResponseExpense] | dict:
    expenses = await ExpenseDAO.find_all(db_session)
    if not expenses:
        return {"message": "NOT found"}
    return [ResponseExpense.model_validate(expense) for expense in expenses]


@router.post("/")
async def create_expense(
    expense: CreateExpense,
    db_session: DB_SESSION
):
    expense_to_db = await ExpenseDAO.add(db_session, **expense.model_dump())
    return {"message": "Expense was added",
            "expense": ResponseExpense.model_validate(expense_to_db)}


@router.delete("/{data_id}")
async def delete_expense(
    data_id: int,
    db_session: DB_SESSION
):
    try:
        await ExpenseDAO.delete(db_session, data_id=data_id)
    except Exception as e:
        await db_session.rollback()
        return e
    return {"message":
            "Expense was deleted"}


@router.get("/categories")
async def get_categories(
        db_session: DB_SESSION):
    categories = await ExpenseDAO.find_categories(db_session)
    return categories
