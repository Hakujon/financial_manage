from httpx import AsyncClient
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
url_api = "http://localhost:8000/finance/"
from bot.schemas import ExpenseFilter

now = datetime.now()
one_week_ago = datetime.now() - timedelta(weeks=1)
one_month_ago = datetime.now() - relativedelta(months=1)

this_week_start = datetime.now() - timedelta(days=now.weekday())
this_week_start = this_week_start.replace(hour=0, minute=0, second=0, microsecond=0)

this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def format_expense(expense: dict):
    created_at = datetime.fromisoformat(expense["created_at"]).strftime(
        "%d.%m.%Y"
        )
    return f"{created_at}\n {expense['category']} - {expense['amount']}"


async def get_exp_for_time(start_date: datetime,
                           end_date: datetime | None = None):
    if end_date:
        query = f"{url_api}?start_date={start_date}&end_date={end_date}"
    else:
        query = f"{url_api}?start_date={start_date}"
    async with AsyncClient() as client:
        response = await client.get(query)
        response = response.json()
        if isinstance(response, list):
            data = [format_expense(expense) for expense in response]
        else:
            data = response.get("message", "No date")
    return data


async def get_last_week_exp():
    expenses = await get_exp_for_time(one_week_ago)
    return expenses


async def get_last_month_exp():
    expenses = await get_exp_for_time(one_month_ago)
    return expenses


async def get_categories():
    async with AsyncClient() as client:
        response = await client.get(
            f"{url_api}categories"
        )
        response = response.json()
        if isinstance(response, list):
            return response
        else:
            raise Exception


async def get_exp_by_filters(filter: ExpenseFilter) -> list[str] | str:
    params = {
        k: v.isoformat() if isinstance(v, datetime) else v
        for k, v in filter.model_dump(exclude_none=True).items()
    }

    async with AsyncClient() as client:
        response = await client.get(url=url_api, params=params)
        result = response.json()

    if isinstance(result, list):
        return [format_expense(expense) for expense in result]
    return result.get("message", "No data")


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


async def get_this_month_exp() -> list[str] | str:
    filter = create_filter(start_date=this_month_start)
    expenses = await get_exp_by_filters(filter=filter)
    return expenses


async def get_this_week_exp() -> list[str] | str:
    filter = create_filter(start_date=this_week_start)
    expenses = await get_exp_by_filters(filter=filter)
    return expenses


async def get_category_exp(category: str) -> list[str] | str:
    filter = create_filter(category=category)
    expenses = await get_exp_by_filters(filter=filter)
    return expenses
