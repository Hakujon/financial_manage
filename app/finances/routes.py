from typing import Annotated
from fastapi import APIRouter

from app.finances.models import Expense
from app.finances.schemas import BaseExpense
from app.finances.dao import ExpenseDAO
from app.database import DB_SESSION


router = APIRouter(prefix="/finance", tags=["Work with Expenses"])


@router.get("/")
async def get_expenses_by_filter(

)