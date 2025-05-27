from app.database import Base, int_pk
from sqlalchemy.orm import Mapped, relationship

class Family(Base):
    id: Mapped[int_pk]
