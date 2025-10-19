from typing import Any
from src.schemas.schemas import CreatePlan, BaseCategory


def is_float_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def is_expense_format(text: Any) -> str:
    parts = text.strip().split()

    if len(parts) < 2:
        raise ValueError("Wrong format")

    first_word, second_word = parts[0], parts[1]

    if (
        is_float_number(first_word)
        or is_float_number(second_word)
    ):
        return text

    raise ValueError("Wrong format")


def is_plan_format(text: Any) -> CreatePlan:
    parts = text.strip().split()

    if 3 < len(parts) < 2:
        raise ValueError("Wrong format")

    category_name = parts[0]
    category = BaseCategory(category_name=category_name)
    planned_amount = parts[1]
    start_date = parts[2] if len(parts) > 2 else None
    return CreatePlan(
        category=category,
        planned_amount=float(planned_amount),
        start_date=start_date
    )
