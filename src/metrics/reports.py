from datetime import datetime
from typing import Callable

from pydantic import BaseModel
from src.api.model.training import Training

from src.metrics.queue import QUEUE


MESSAGE_GROUP_ID = "metrics"
SERVICE_NAME = "trainings"
CMD_CREATED = "trainingCreated"


class TrainingCreationReport(BaseModel):
    service: str = SERVICE_NAME
    command: str = CMD_CREATED
    timestamp: datetime
    attrs: Training

    @classmethod
    def from_now(cls, attrs: Training) -> "TrainingCreationReport":
        return TrainingCreationReport(timestamp=datetime.now(), attrs=attrs)


def report_training_creation(training: Training) -> None:
    body = TrainingCreationReport.from_now(attrs=training).json()

    if QUEUE.url.endswith(".fifo"):
        # Send message with SQS FIFO-only parameters
        _ = QUEUE.send_message(
            MessageBody=body,
            # MessageDeduplicationId and MessageGroupId only for FIFO queues
            MessageDeduplicationId=f"{SERVICE_NAME}-{CMD_CREATED}-{training.id}",
            MessageGroupId=MESSAGE_GROUP_ID,
        )
    else:
        _ = QUEUE.send_message(
            MessageBody=body,
        )


def get_reporter() -> Callable[[Training], None]:
    return report_training_creation
