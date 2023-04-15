from typing import Optional
from pydantic import BaseModel, Field
from src.api.model.utils import make_all_required

from src.db.model.training import TrainingType


class TrainingBase(BaseModel):
    title: Optional[str] = Field(
        title="The training's title", min_length=2, max_length=30, default=None
    )
    description: Optional[str] = Field(
        title="The training's description", max_length=300, default=None
    )
    type: Optional[TrainingType] = Field(
        title="The training's type", default=None
    )
    difficulty: Optional[int] = Field(
        title="The training's difficulty", ge=0, le=10, default=None
    )

    # https://docs.pydantic.dev/usage/models/#orm-mode-aka-arbitrary-class-instances
    class Config:
        orm_mode = True


class AllRequiredTrainingBase(TrainingBase):
    pass


make_all_required(AllRequiredTrainingBase)


class CreateTraining(AllRequiredTrainingBase):
    pass


class PatchTraining(TrainingBase):
    pass


class Training(AllRequiredTrainingBase):
    id: int = Field(title="The training's id")
