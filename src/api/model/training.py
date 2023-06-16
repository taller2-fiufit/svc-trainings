from datetime import datetime
from typing import List, Literal, Optional, Union
from fastapi import Query
from pydantic import BaseModel, ConstrainedStr, Field
from src.api.model.utils import OrmModel, make_all_required

from src.common.model import TrainingType


MIN_DIFFICULTY = 0
MAX_DIFFICULTY = 10


# https://github.com/pydantic/pydantic/issues/156
class Multimedia(ConstrainedStr):
    max_length = 255
    strip_whitespace = True

    class Config:
        orm_mode = True


class Goal(OrmModel):
    name: str = Field(
        title="Name",
        description="The goal's name",
        min_length=1,
        max_length=30,
    )
    description: str = Field(
        title="Description",
        description="The goal's description",
        max_length=300,
        default=None,
    )


class TrainingBase(OrmModel):
    title: Optional[str] = Field(
        title="Title",
        description="The training's main title",
        min_length=2,
        max_length=30,
        default=None,
    )
    description: Optional[str] = Field(
        title="Description",
        description="The training's description",
        max_length=300,
        default=None,
    )
    type: Optional[TrainingType] = Field(
        title="Type",
        description="The training's type. If it is a walk, is running, etc.",
        default=None,
    )
    difficulty: Optional[int] = Field(
        title="Difficulty",
        description="The training's difficulty",
        ge=MIN_DIFFICULTY,
        le=MAX_DIFFICULTY,
        default=None,
    )
    multimedia: Optional[List[Multimedia]] = Field(
        title="Multimedia resources",
        description="The training's multimedia resources (images or videos)",
        max_items=8,
        default=None,
    )
    goals: Optional[List[Goal]] = Field(
        title="Goals",
        description="The training's goals. "
        "This should be fulfilled to complete the training plan",
        max_items=64,
        unique_items=True,
        default=None,
    )


class AllRequiredTrainingBase(TrainingBase):
    pass


make_all_required(AllRequiredTrainingBase)


class CreateTraining(AllRequiredTrainingBase):
    pass


class PatchTraining(TrainingBase):
    pass


class Training(AllRequiredTrainingBase):
    id: int = Field(title="ID", description="The training's ID")
    author: int = Field(
        title="Author's ID", description="The training author's ID"
    )
    blocked: bool = Field(
        title="Is blocked?",
        description="True if the training is blocked, false if it isn't",
    )
    created_at: datetime = Field(
        title="Time of creation",
        description="The timestamp of this training's creation",
        alias="createdAt",
    )
    score: float = Field(
        title="Average score",
        description="Average score of training",
    )
    score_amount: int = Field(
        title="Amount of scores",
        description="The amount of times this training was scored by users",
    )


class BlockStatus(BaseModel):
    blocked: bool = Field(
        title="Is blocked?",
        description="True if the training is blocked, false if it isn't",
    )


class ScoreBody(BaseModel):
    score: float = Field(
        title="Score",
        description="Score given to training by user",
        ge=0.0,
        le=5.0,
    )


class FilterParams(BaseModel):
    offset: int = Field(Query(0, title="Query initial offset"))
    limit: int = Field(Query(100, title="Query item limit"))
    author: Optional[Union[Literal["me"], int]] = Field(
        Query(None, title="Author filter")
    )
    type: Union[TrainingType, Literal["all"]] = Field(
        title="Type filter",
        default="all",
    )
    mindiff: int = Field(
        Query(MIN_DIFFICULTY, title="Minimum training difficulty (inclusive)")
    )
    maxdiff: int = Field(
        Query(
            MAX_DIFFICULTY + 1, title="Maximum training difficulty (exclusive)"
        )
    )
    blocked: Union[bool, Literal["all"]] = Field(
        Query(False, title="Return blocked trainings")
    )
