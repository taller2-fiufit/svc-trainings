from datetime import datetime
from typing import Callable

from pydantic import BaseModel

from src.metrics.queue import QUEUE


MESSAGE_GROUP_ID = "metrics"
SERVICE_NAME = "trainings"
CMD_CREATED = "trainingCreated"


class TrainingCreationReport(BaseModel):
    service: str = SERVICE_NAME
    command: str = CMD_CREATED
    timeStamp: datetime

    @classmethod
    def from_now(cls) -> "TrainingCreationReport":
        return TrainingCreationReport(timeStamp=datetime.now())


def report_training_creation(id: int) -> None:
    body = TrainingCreationReport.from_now().json()

    if QUEUE.url.endswith(".fifo"):
        # Send message with SQS FIFO-only parameters
        _ = QUEUE.send_message(
            MessageBody=body,
            # MessageDeduplicationId and MessageGroupId only for FIFO queues
            MessageDeduplicationId=f"{SERVICE_NAME}-{CMD_CREATED}-{id}",
            MessageGroupId=MESSAGE_GROUP_ID,
        )
    else:
        _ = QUEUE.send_message(
            MessageBody=body,
        )


def get_reporter() -> Callable[[int], None]:
    return report_training_creation
