from typing import Optional
from datetime import datetime
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


class CreateExpense(BaseExpense):
    pass


class ResponseExpense(BaseExpense):
    id: int
    created_at: Optional[datetime] = Field(
        None, description="Дата создания"
    )


class FilterExpense(BaseModel):
    start_amount: Optional[float] = Field(
        None, description="Минимальная сумма"
    )
    head_amount: Optional[float] = Field(
        None, description="Максимальная сумма"
    )
    category: Optional[str] = Field(
        None, description="Категория"
    )
    start_date: Optional[datetime] = Field(
        None, description="Начальная дата"
    )
    end_date: Optional[datetime] = Field(
        None, description="Конечная дата"
    )
