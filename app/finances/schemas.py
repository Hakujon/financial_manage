from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseExpense(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    amount: float
