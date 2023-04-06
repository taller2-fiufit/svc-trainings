import enum
from enum import auto
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
