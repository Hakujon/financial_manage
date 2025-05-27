from app.dao.base import BaseDAO
from app.finances.models import Expense


class ExpenseDAO(BaseDAO):
    model = Expense
