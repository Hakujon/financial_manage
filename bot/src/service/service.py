from httpx import AsyncClient
from datetime import datetime, timedelta
from src.schemas.schemas import ExpenseFilter, ExpenseWriter
from src.core.config import settings

URL = settings.URL_API

now = datetime.now()
this_week_start = now - timedelta(days=now.weekday())
this_week_start = this_week_start.replace(hour=0,
                                          minute=0,
                                          second=0,
                                          microsecond=0)
this_month_start = now.replace(day=1,
                               hour=0,
                               minute=0,
                               second=0,
                               microsecond=0)


def is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def format_expense_to_response(expense: dict) -> str:
    created_at = datetime.fromisoformat(
        expense["created_at"]).strftime(
            "%d.%m.%Y"
        )
    if expense["description"] is None:
        return (
            f"\n{created_at}\n"
            f"{expense['amount'] - {expense['category']['category_name']}}"
        )
    return (
        f"\n{created_at}\n"
        f"{expense['amount']} - {expense['category']['category_name']}\n"
        f"{expense['description']}"
    )


def format_expense_to_write(text: str) -> ExpenseWriter:
    text = text.strip()
    parts = text.split()
    if is_number(parts[0]):
        amount = float(parts[0])
        category = parts[1]
    elif is_number(parts[1]):
        amount = float(parts[1])
        category = parts[0]
    else:
        raise ValueError(
            "Wrong format"
        )
    description = "".join(parts[2:]) if len(parts) > 2 else None
    expense = ExpenseWriter(
        amount=amount,
        category=category,
        description=description
    )
    return expense


def create_filter(
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        category: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None
) -> ExpenseFilter:
    return ExpenseFilter(
        start_date=start_date,
        end_date=end_date,
        category=category,
        min_amount=min_amount,
        max_amount=max_amount
    )


async def get_categories():
    async with AsyncClient() as client:
        response = await client.get(
            url=f"{URL}/categories"
        )
        response = response.json()
        if isinstance(response, list):
            response.append("All")
            return response
        else:
            raise Exception


async def get_exp_by_filters(
            filter: ExpenseFilter
        ) -> list[str] | str:
    params = {
        k: v.isoformat() if isinstance(v, datetime) else v
        for k, v in filter.model_dump(exclude_none=True).items()
    }
    async with AsyncClient() as client:
        if URL:
            response = await client.get(url=URL,
                                        params=params)
            result = response.json()
        if isinstance(result, list):
            return [
                format_expense_to_response(expense) for expense in result
                ]
        return [result.get("message", "No data")]


async def get_this_week_exp() -> list[str] | str:
    filter = create_filter(start_date=this_week_start)
    expenses = await get_exp_by_filters(filter=filter)
    return expenses


async def get_this_month_exp() -> list[str] | str:
    filter = create_filter(start_date=this_month_start)
    expenses = await get_exp_by_filters(filter=filter)
    return expenses


async def get_exp_by_category(category: str) -> list[str] | str:
    filter = create_filter(category=category)
    expenses = await get_exp_by_filters(filter=filter)
    return expenses


async def create_expense(
    text: str
) -> None:
    expense = format_expense_to_write(text=text)
    async with AsyncClient() as client:
        if URL:
            await client.post(
                url=URL,
                json=expense.model_dump()
            )
