from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseExpense(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    amount: float = Field(
        ..., ge=1, description="Сумма"
    )
    category: str = Field(
        ..., min_length=3, max_length=35, description="Категория"
        )
    description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=80,
        description="Краткое описание"
    )
    family_id: int = Field(...,
                           description="Номер семейства")


class CreateExpense(BaseExpense):
    pass


class ResponseExpense(BaseExpense):
    id: int
