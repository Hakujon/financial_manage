from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.inspection import inspect
from datetime import datetime
from src.database import (
    Base, int_pk, str_not_null,
    str_null, created_at, updated_at)


class Category(Base):
    id: Mapped[int_pk]
    category_name: Mapped[str_not_null]
    created_at: Mapped[created_at]


class Expense(Base):
    id: Mapped[int_pk]
    amount: Mapped[float]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categorys.id"),
        nullable=False
    )
    category: Mapped["Category"] = relationship()
    description: Mapped[str_null]
    created_at: Mapped[created_at]

    def __str__(self):
        return (f"{self.__class__.__name__} {self.id}")

    def __repr__(self):
        return str(self)

    def to_dict(
        self
    ) -> dict:
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }

    @classmethod
    def from_dict(
        cls,
        data: dict
    ):
        return cls(**data)


class Plan(Base):
    id: Mapped[int_pk]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categorys.id"),
        nullable=False
    )
    category: Mapped["Category"] = relationship()
    planned_amount: Mapped[float]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
