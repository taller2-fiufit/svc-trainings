from pydantic import BaseModel, Field

from src.db.training import TrainingType


class TrainingBase(BaseModel):
    title: str = Field(
        title="The training's title", min_length=2, max_length=30
    )
    description: str = Field(
        title="The training's description", max_length=300
    )
    type: TrainingType = Field(title="The training's type")
    difficulty: int = Field(title="The training's difficulty", ge=0, le=10)

    # https://docs.pydantic.dev/usage/models/#orm-mode-aka-arbitrary-class-instances
    class Config:
        orm_mode = True


class CreateTraining(TrainingBase):
    pass


class Training(TrainingBase):
    id: int = Field(title="The training's id")
