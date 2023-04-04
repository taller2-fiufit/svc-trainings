import enum
from enum import auto
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TrainingType(enum.StrEnum):
    WALK = auto()
    RUNNING = auto()


class DBTraining(Base):
    __tablename__ = "trainings_table"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(30), unique=True, index=True)
    description = Column(String(500))
    type: Column[Enum] = Column(Enum(TrainingType))
    difficulty = Column(Integer)
