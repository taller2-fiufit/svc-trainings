from datetime import datetime
from typing import Any, Callable, Dict

from pydantic import BaseModel
from src.api.model.training import Training

from src.metrics.queue import QUEUE


MESSAGE_GROUP_ID = "metrics"
SERVICE_NAME = "trainings"


class Report(BaseModel):
    service: str = SERVICE_NAME
    command: str
    timestamp: datetime
    attrs: Dict[str, Any]


class TrainingCreatedReport(Report):
    command: str = "trainingCreated"

    @classmethod
    def from_now(cls, training: Training) -> Report:
        return cls(timestamp=datetime.now(), attrs=training.dict())


def report_training_created(training: Training) -> None:
    body = TrainingCreatedReport.from_now(training).json()

    _ = QUEUE.send_message(
        MessageBody=body,
    )


class TrainingFavoritedReport(Report):
    command: str = "trainingFavorited"

    @classmethod
    def from_now(cls, user_id: int, training_id: int) -> Report:
        attrs = {"user_id": user_id, "training_id": training_id}
        return cls(timestamp=datetime.now(), attrs=attrs)


def report_training_favorited(user_id: int, training_id: int) -> None:
    body = TrainingFavoritedReport.from_now(user_id, training_id).json()

    _ = QUEUE.send_message(
        MessageBody=body,
    )


def get_training_creation_reporter() -> Callable[[Training], None]:
    return report_training_created


def get_training_favorited_reporter() -> Callable[[int, int], None]:
    return report_training_favorited
