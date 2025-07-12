from sqlalchemy.orm import Mapped
from app.database import Base, int_pk, str_not_null, str_null


class Expense(Base):
    id: Mapped[int_pk]
    amount: Mapped[float]
    category: Mapped[str_not_null]
    description: Mapped[str_null]
    # family_id: Mapped[int] = mapped_column(
    #     ForeignKey("familys.id"),
    #     nullable=False
    # )
    # family: Mapped["Family"] = relationship(
    #     "Family"
    # )

    def __str__(self):
        return (f"{self.__class__.__name__} {self.id}")

    def __repr__(self):
        return str(self)
