from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.database import Base, int_pk, str_not_null
from app.users.models import Family


class Expense(Base):
    id: Mapped[int_pk]
    name: Mapped[str_not_null]
    amount: Mapped[float]
    category: Mapped[str_not_null]
    family_id: Mapped[int] = mapped_column(
        ForeignKey("familys.id"),
        nullable=False
    )
    family: Mapped["Family"] = relationship(
        "Family"
    )
    category: Mapped[str_not_null]

    def __str__(self):
        return (f"{self.__class__.__name__} {self.id}"
                f"{self.name}"
        )

    def __repr__(self):
        return str(self)
