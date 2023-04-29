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
    timestamp: datetime


def report_training_creation(id: int) -> None:
    body = TrainingCreationReport(timestamp=datetime.now()).json()
    # Send message to SQS queue
    _ = QUEUE.send_message(
        MessageBody=body,
        # MessageAttributes={},
        MessageDeduplicationId=f"{SERVICE_NAME}-{CMD_CREATED}-{id}",
        MessageGroupId=MESSAGE_GROUP_ID,
    )


def get_reporter() -> Callable[[int], None]:
    return report_training_creation
