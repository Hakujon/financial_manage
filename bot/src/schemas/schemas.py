from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BaseCategory(BaseModel):
    category_name: str = Field(
        ..., min_length=3, max_length=15,
        description="Название категории"
    )


class BaseExpense(BaseModel):
    amount: float = Field(
        ..., ge=1, description="Сумма"
    )
    category: BaseCategory
    description: Optional[str] = Field(
        None,
        max_length=80,
        description="Описание расхода"
    )


class BasePlan(BaseModel):
    category: BaseCategory


class CreateExpense(BaseExpense):
    pass


class CreatePlan(BasePlan):
    start_date: Optional[datetime] = Field(
        None,
        description="Начало промежутка планирования"
    )
    planned_amount: Optional[float] = Field(
        None,
        ge=1,
        description="Планируемая сумма"
    )


class ResponseExpense(BaseExpense):
    id: int
    created_at: datetime = Field(
        ...,
        description="Дата создания"
    )


class ResponsePlan(BasePlan):
    id: int
    start_date: datetime = Field(
        ...,
        description="Начало промежутка планирования"
    )
    end_date: datetime = Field(
        ...,
        description="Конец промежутка планирования"
    )
    planned_amount: float = Field(
        ...,
        ge=1,
        description="Планируемая сумма"
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания плана"
    )
    updated_at: datetime = Field(
        ...,
        description="Дата последнего обновления"
    )


class ExpenseWriter(BaseModel):
    amount: float
    category: BaseCategory
    description: Optional[str] = None


class ExpenseFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
