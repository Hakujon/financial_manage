from httpx import AsyncClient
from datetime import datetime, timedelta
from src.schemas.schemas import (
    ExpenseFilter, ExpenseWriter,
    CreatePlan, BaseCategory
)
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
            f"{expense['amount']} - {expense['category']['category_name']}"
        )
    return (
        f"\n{created_at}\n"
        f"{expense['amount']} - {expense['category']['category_name']}\n"
        f"{expense['description']}"
    )


def format_plan_to_response(plan: dict) -> str:
    category = plan["category"]["category_name"]
    start_date = plan["start_date"]
    end_date = plan["end_date"]
    planned_amount = plan["planned_amount"]
    return (
        f"Новый план\n Категория: {category}\n"
        f"Начало промежутка: {start_date}\n"
        f"Конец промежутка: {end_date}\n"
        f"Планируемая сумма: {planned_amount}"
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
        category=BaseCategory(category_name=category),
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
            categorys = [BaseCategory.model_validate(category) for category in response]
            category_names = [cat.category_name for cat in categorys]
            category_names.append("All")
            return category_names
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
            response = await client.get(url=f"{URL}/expenses",
                                        params=params)
            result = response.json()
            print(result)
            print(type(result))
        # if isinstance(result, list):
        #     result_list = [format_expense_to_response(expense) for expense in result]
        #     print(result_list)
        #     return result_list
        if isinstance(result, list):
            result_list = []
            for expense in result:
                try:
                    formatted = format_expense_to_response(expense)
                    result_list.append(formatted)
                except Exception as e:
                    print("❌ Ошибка при форматировании:", expense)
                    print(e)
            print(result_list)
            return result_list
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


async def get_remaining_of_category(
        category: str) -> dict:
    async with AsyncClient() as client:
        if URL:
            response = await client.get(
                url=f"{URL}/plans/remains",
                params={"category": category}
            )

            plan = response.json()

    return plan


async def create_expense(
    text: str
) -> str:
    expense = format_expense_to_write(text=text)
    async with AsyncClient() as client:
        try:
            if URL:
                response = await client.post(
                    url=f"{URL}/expenses",
                    json=expense.model_dump()
                )
                new_expense = response.json()
                print(new_expense)
        except Exception as e:
            raise e
    async with AsyncClient() as client:
        if URL:
            remaining_plan = await get_remaining_of_category(
                category=expense.category.category_name
            )

    expense_str = format_expense_to_response(
        expense=new_expense
    )
    expense_with_plan = (
        f"{expense_str}\n"
        f"Планировалось в категории {remaining_plan['planned_amount']}"
        f"Осталось {remaining_plan['remaining']}"
    )
    return expense_with_plan


async def create_plan(
        plan: CreatePlan
) -> str:
    async with AsyncClient() as client:
        if URL:
            response = await client.post(
                url=f"{URL}/plans",
                json=plan.model_dump_json()
            )
            new_plan = response.json()
    return format_plan_to_response(plan=new_plan)


async def get_plan_of_category(category: str) -> str:
    try:
        async with AsyncClient() as client:
            if URL:
                response = await client.get(
                    url=f"{URL}/plans",
                    params={"category_name": category}
                )
                plan = response.json()
        return format_plan_to_response(plan=plan)
    except Exception as e:
        raise e
