from sqlalchemy import (
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.db.model.base import Base
from src.db.model.training import DBTraining


class DBFavorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    user_id: Mapped[int] = mapped_column(Integer)

    training: Mapped[DBTraining] = relationship()
