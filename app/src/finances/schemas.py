from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class BaseCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    category_name: str = Field(
        ..., min_length=3, max_length=15,
        description="Название категории"
    )


class BaseExpense(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              )
    amount: float = Field(
        ..., ge=1, description="Сумма"
    )
    category: BaseCategory


class BasePlan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: BaseCategory


class CreateCategory(BaseCategory):
    pass


class CreateExpense(BaseExpense):
    description: Optional[str] = Field(
        None,
        min_length=0,
        max_length=80,
        description="Краткое описание"
    )


class CreatePlan(BasePlan):
    start_date: Optional[datetime] = Field(
        None,
        description="Начало промежутка планирования"
    )
    planned_amount: Optional[float] = Field(
        None,
        description="Планируемая сумма"
    )


class ResponseExpense(BaseExpense):
    id: int
    description: Optional[str] = Field(
        None,
        min_length=0,
        max_length=80,
        description="Краткое описание"
    )
    created_at: datetime = Field(
        ..., description="Дата создания"
    )


class ResponseCategory(BaseCategory):
    id: int


class ResponsePlan(BasePlan):
    id: int
    start_date: datetime = Field(
        ..., description="Начало промежутка планирования"
    )
    end_date: datetime = Field(
            ..., description="Конец промежутка планирования"
    )
    planned_amount: float = Field(
        ..., description="Планируемая сумма"
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания плана"
    )
    updated_at: datetime = Field(
        ...,
        description="Дата последнего изменения"
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


class FilterCategory(BaseModel):
    category_name: str = Field(
        ..., description="Название категории"
    )
