import enum
from enum import auto
from typing import Optional
from sqlalchemy import Column, Integer, String, Enum

from src.db.model.base import Base


class TrainingType(enum.StrEnum):
    WALK = auto()
    RUNNING = auto()


class DBTraining(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(30), unique=True, index=True)
    description = Column(String(500))
    type: Column[Enum] = Column(Enum(TrainingType))
    difficulty = Column(Integer)

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[TrainingType] = None,
        difficulty: Optional[int] = None,
    ) -> None:
        self.title = title or self.title  # type: ignore
        self.description = description or self.description  # type: ignore
        self.type = type or self.type  # type: ignore
        self.difficulty = difficulty or self.difficulty  # type: ignore
