from aiogram.filters import BaseFilter
from aiogram.types import Message


class ExpenseFormatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False

        parts = message.text.strip().split()

        if len(parts) < 2:
            return False

        first_word, second_word = parts[0], parts[1]

        if (
            is_number(first_word)
            or is_number(second_word)
        ):
            return True

        return False


def is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False
