from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Enum,
    func,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.api.model.training import CreateTraining, Goal, Multimedia, Training

from src.common.model import TrainingType
from src.db.model.base import Base


SCORE_SCALE: int = 100


class DBMultimedia(Base):
    __tablename__ = "training_multimedias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    url: Mapped[str] = mapped_column(String(255))


def multimedia_api_to_db(multimedia: List[Multimedia]) -> List[DBMultimedia]:
    return [DBMultimedia(url=str(m)) for m in multimedia]


def multimedia_db_to_api(
    multimedia: List[DBMultimedia],
) -> List[Multimedia]:
    return [Multimedia(m.url) for m in multimedia]


class DBGoal(Base):
    __tablename__ = "training_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(300))


def goals_api_to_db(goals: List[Goal]) -> List[DBGoal]:
    return [DBGoal(name=g.name, description=g.description) for g in goals]


def goals_db_to_api(db_goals: List[DBGoal]) -> List[Goal]:
    return [Goal(name=g.name, description=g.description) for g in db_goals]


class DBScore(Base):
    __tablename__ = "training_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"))
    author: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_api(
        cls, training_id: int, author: int, score: float
    ) -> "DBScore":
        int_score = round(score * SCORE_SCALE)
        return cls(training_id=training_id, author=author, score=int_score)

    def get_api_score(self) -> float:
        float_score = self.score / SCORE_SCALE
        return float_score

    def update_score(self, score: float) -> None:
        self.score = round(score * SCORE_SCALE)


class DBTraining(Base):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author: Mapped[int] = mapped_column(Integer)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    title: Mapped[str] = mapped_column(String(30), index=True, unique=True)
    description: Mapped[str] = mapped_column(String(300))
    type: Mapped[TrainingType] = mapped_column(Enum(TrainingType))
    difficulty: Mapped[int] = mapped_column(Integer)
    multimedia: Mapped[List[DBMultimedia]] = relationship(
        cascade="all, delete-orphan",
        lazy="immediate",
    )
    goals: Mapped[List[DBGoal]] = relationship(
        cascade="all, delete-orphan",
        lazy="immediate",
    )
    scores: Mapped[List[DBScore]] = relationship(
        cascade="all, delete-orphan",
        lazy="immediate",
    )

    @classmethod
    def from_api_model(
        cls,
        author: int,
        training: CreateTraining,
    ) -> "DBTraining":
        # this never happens, but mypy needs reassurance
        assert training.multimedia is not None
        assert training.goals is not None

        db_multimedia = multimedia_api_to_db(training.multimedia)
        db_goals = goals_api_to_db(training.goals)

        kwargs = {
            **training.dict(),
            "multimedia": db_multimedia,
            "goals": db_goals,
            "scores": [],
        }

        return cls(author=author, **kwargs)

    def to_api_model(self) -> Training:
        multimedia = multimedia_db_to_api(self.multimedia)
        goals = goals_db_to_api(self.goals)

        score_amount = len(self.scores)

        if score_amount == 0:
            score = 0.0
        else:
            score_total = sum((s.score for s in self.scores))
            score = score_total / (score_amount * SCORE_SCALE)

        return Training(
            id=self.id,
            author=self.author,
            blocked=self.blocked,
            created_at=self.created_at,  # type: ignore
            title=self.title,
            description=self.description,
            type=self.type,
            difficulty=self.difficulty,
            multimedia=multimedia,
            goals=goals,
            score=score,
            score_amount=score_amount,
        )

    def update(
        self,
        author: Optional[int] = None,
        blocked: Optional[bool] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[TrainingType] = None,
        difficulty: Optional[int] = None,
        multimedia: Optional[List[str]] = None,
        goals: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.author = author or self.author
        self.blocked = blocked or self.blocked
        self.title = title or self.title
        self.description = description or self.description
        self.type = type or self.type
        self.difficulty = difficulty or self.difficulty
        if multimedia is not None:
            self.multimedia = [DBMultimedia(url=m) for m in multimedia]
        if goals is not None:
            self.goals = [
                DBGoal(name=g["name"], description=g["description"])
                for g in goals
            ]
