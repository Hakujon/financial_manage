from typing import Annotated
from datetime import datetime

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncSession,
                                    async_sessionmaker, AsyncAttrs)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, declared_attr, mapped_column
)

from app.config import settings

DATABASE_URL = settings.get_db_url()

async_engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


DB_SESSION = Annotated[AsyncSession, Depends(get_db)]

int_pk = Annotated[int, mapped_column(primary_key=True)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null = Annotated[str, mapped_column(nullable=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(
    server_default=func.now(),
    onupdate=datetime.now
)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
