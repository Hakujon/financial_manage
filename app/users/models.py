from app.database import Base, int_pk, str_not_null
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column


class Association(Base):
    family_id: Mapped[int] = mapped_column(
        ForeignKey("familys.id"), primary_key=True
        )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
        )


class Family(Base):
    id: Mapped[int_pk]
    name: Mapped[str_not_null]
    users: Mapped[list["User"]] = relationship(
        secondary='associations',
        back_populates="users"
    )


class User(Base):
    id: Mapped[int_pk]
    username: Mapped[str_not_null]
    telegram_id: Mapped[int]
    familys: Mapped[list["Family"]] = relationship(
        secondary="associations",
        back_populates="users",
        lazy="selectin"
    )

    def __repr__(self):
        return f"{self.__class__.__name__} id={self.id}"
